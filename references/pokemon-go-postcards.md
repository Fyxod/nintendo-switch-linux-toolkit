# Pokémon GO postcards and Coin Bag

## Choose the path explicitly

The supported path uses a physical Nintendo Switch or Switch 2 with an updated Pokémon Scarlet/Violet installation. Follow Nintendo's current instructions: <https://en-americas-support.nintendo.com/app/answers/detail/a_id/61360/>.

Ryujinx does not provide the phone-facing Bluetooth feature needed for this connection. Installing the game in an emulator does not make the laptop a supported Switch receiver.

If the user explicitly requests the community helper, explain that it is separate from the emulator and emulates only the Bluetooth postcard exchange for GO rewards. The open-source project used in the field session is <https://github.com/na-ji/pokemon-go-coin-bag>. Review its current source and protocol documentation before use because it can change. Do not vendor its signing constants, protocol implementation, browser profile, or generated application ID into another repository.

## Two independent BLE sessions

Pairing and postcard sending are separate connections:

1. In GO settings, connect to Nintendo Switch; start the helper; select the advertising phone. Successful registration saves a Switch/application identity.
2. In GO's Postcard Book, choose a postcard and select Send to Nintendo Switch; start the helper again; select the phone again. This second session performs the exchange.

The BLE link normally closes after each successful operation. That disconnect is not proof that pairing was lost. Confirm success from the phone and the presence/recharge of the Coin Bag.

## Dedicated browser profile

Use a dedicated browser profile so the helper's `localStorage` identity persists. Never clear that profile during an active or previously successful pairing unless the user explicitly wants to pair from scratch.

On Brave builds that gate Web Bluetooth, the working feature name observed was:

```text
--enable-features=BraveWebBluetoothAPI
--enable-experimental-web-platform-features
```

Do not copy an internal C++ symbol name with a leading `k`; that produced “Web Bluetooth API globally disabled.” Browser feature names can change, so verify against the current build.

Web Bluetooth requires a secure context and a user gesture. `localhost` is treated as secure. `navigator.bluetooth.requestDevice()` must be called directly from a click handler before an `await`; opening a picker later in an async chain can lose user activation.

## “Connect another device” behavior

When extending a helper UI, preserve these invariants:

- A new button creates a fresh browser device request without deleting the stored application identity.
- The click synchronously aborts the active session, removes notification listeners, and disconnects its GATT link.
- Every async continuation checks a unique current-session token so an old attempt cannot overwrite new status.
- If the same `BluetoothDevice` object is reused, a late completion from the old attempt must not disconnect the new session.
- A modal browser chooser cannot be programmatically replaced; the user must cancel the open chooser first.
- A cancelled chooser returns the UI to a ready state.
- Preserve ambiguity: if the final indication times out, tell the user to check GO rather than claiming the postcard was received.

## Diagnosis by protocol stage

Log only stage names and errors. Do not print nonces, transaction IDs, signing values, saved identities, device addresses, or trainer names in shared output.

Useful stages are: chooser, connect, primary-service discovery, characteristic discovery, protocol read, player-name read, mode read, application-ID write, initial-nonce write, DATA subscription, first DATA indication, completion write, final indication, and final-nonce write.

A strong BLE signal and successful service discovery followed by a 30-second protocol-read failure with ATT error `0x0e` points to the phone's GATT server/session, not the browser UI. A read-only BlueZ probe can confirm this. The field fix was:

1. Force-stop Pokémon GO.
2. Turn phone Bluetooth off and back on.
3. Disconnect watches, earbuds, or other phone Bluetooth accessories.
4. Reopen GO and keep it in the foreground.
5. Start Send to Nintendo Switch from the Postcard Book.
6. Start a fresh receiver connection without clearing the saved pairing identity.

Do not clear GO storage or remove the saved Switch pairing for this recovery.

## Safe automation

The browser device chooser protects access to nearby hardware. Automation may select a device only when the user has requested the connection and exactly one filtered GO device is offered. If multiple devices appear, stop rather than guessing.

Use `scripts/coin-bag-probe.py` only when no browser helper is connected. It reads the protocol and mode characteristics and disconnects; it never performs pairing or postcard writes.
