/**
 * Generic Web Bluetooth session ownership for a "connect another device" UI.
 * This file deliberately contains no game protocol, identity, signing material,
 * device address, or application data. Integrate runSession() in the host app.
 */
export class FreshDeviceSessionManager {
  #current = null;

  get busy() {
    return this.#current !== null;
  }

  /** Call directly from a click handler so requestDevice keeps user activation. */
  start(requestOptions, runSession) {
    const previous = this.#current;
    this.#current = null;
    previous?.cancel();

    const session = new OwnedSession(this);
    this.#current = session;
    // Do not insert an await before requestDevice().
    const devicePromise = navigator.bluetooth.requestDevice(requestOptions);
    return session.run(devicePromise, runSession);
  }

  cancel() {
    const previous = this.#current;
    this.#current = null;
    previous?.cancel();
  }

  owns(session) {
    return this.#current === session;
  }

  canDisconnect(session, device) {
    // A late completion from a cancelled attempt must not disconnect the same
    // BluetoothDevice after a newer session has adopted it.
    return !this.#current || this.#current === session || this.#current.device !== device;
  }

  release(session) {
    if (this.#current === session) this.#current = null;
  }
}

class OwnedSession {
  #manager;
  #controller = new AbortController();
  #cleanups = new Set();
  #device = null;
  #closed = false;

  constructor(manager) {
    this.#manager = manager;
  }

  get signal() {
    return this.#controller.signal;
  }

  get device() {
    return this.#device;
  }

  assertCurrent() {
    this.signal.throwIfAborted();
    if (!this.#manager.owns(this)) {
      throw new DOMException("Previous session cleared", "AbortError");
    }
  }

  addCleanup(cleanup) {
    this.#cleanups.add(cleanup);
    return () => this.#cleanups.delete(cleanup);
  }

  async wait(promise) {
    this.assertCurrent();
    const aborted = new Promise((_, reject) => {
      this.signal.addEventListener("abort", () => reject(this.signal.reason), { once: true });
    });
    const value = await Promise.race([promise, aborted]);
    this.assertCurrent();
    return value;
  }

  cancel() {
    if (this.#closed) return;
    this.#closed = true;
    if (!this.signal.aborted) {
      this.#controller.abort(new DOMException("Previous session cleared", "AbortError"));
    }
    for (const cleanup of [...this.#cleanups]) cleanup();
    this.#cleanups.clear();
    if (this.#device && this.#manager.canDisconnect(this, this.#device)) {
      try {
        this.#device.gatt?.disconnect();
      } catch {
        // It may already be disconnected.
      }
    }
  }

  async run(devicePromise, runSession) {
    try {
      this.#device = await this.wait(devicePromise);
      return await this.wait(runSession(this.#device, this));
    } finally {
      this.cancel();
      this.#manager.release(this);
    }
  }
}
