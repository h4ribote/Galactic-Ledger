# Transport & Contract System Specification

## 1. Overview
The Transport System allows players to move items between planets using Fleets. The Contract System enables players to issue transport requests to other players, setting rewards and collaterals to ensure safe delivery.

## 2. Data Models

### Fleet
Represents a transport unit owned by a user.
- **Attributes**:
  - `id`: Unique Identifier.
  - `owner_id`: User who owns the fleet.
  - `name`: Name of the fleet.
  - `location_planet_id`: Current location (if stationary).
  - `destination_planet_id`: Target location (if moving).
  - `arrival_time`: When the fleet will arrive at the destination.
  - `status`: `IDLE`, `TRANSIT`.
  - `cargo_capacity`: Max volume of items it can carry.

### Contract
Represents a transport job issued by a player.
- **Attributes**:
  - `id`: Unique Identifier.
  - `issuer_id`: User creating the contract.
  - `contractor_id`: User accepting the contract (Nullable initially).
  - `origin_planet_id`: Where the item is picked up.
  - `destination_planet_id`: Where the item must be delivered.
  - `item_id`: The item to be transported.
  - `quantity`: Amount of the item.
  - `reward_amount`: Credits paid to the contractor upon success.
  - `collateral_amount`: Credits deposited by the contractor as insurance.
  - `duration_seconds`: Allowed time to complete delivery after acceptance.
  - `accepted_at`: Timestamp when the contract was accepted.
  - `deadline`: Timestamp (`accepted_at` + `duration_seconds`) by which delivery must happen.
  - `status`: `OPEN`, `IN_PROGRESS`, `COMPLETED`, `FAILED`, `EXPIRED`.

## 3. Workflow

### A. Contract Creation (Issuer)
1. User specifies: Destination, Item, Quantity, Reward, Collateral, Duration.
2. System checks if User has enough Items and Credits (for Reward).
3. **Action**:
   - Items are removed from User's Planet Inventory and placed in a "Contract Holding" state (or virtually locked).
   - Reward amount is deducted from User's Wallet (Escrowed).
4. Contract created with status `OPEN`.

### B. Contract Acceptance (Contractor)
1. User views open contracts.
2. User accepts a contract.
3. System checks if User has enough Credits for Collateral and a Fleet at the Origin Planet with enough capacity.
4. **Action**:
   - Collateral amount is deducted from Contractor's Wallet (Escrowed).
   - Items are transferred to Contractor's Fleet Inventory.
   - Contract status -> `IN_PROGRESS`.
   - `accepted_at` is set to Now. `deadline` is calculated.

### C. Execution (Transport)
1. Contractor moves their Fleet to the Destination Planet.
2. Standard Fleet movement rules apply (speed, distance).

### D. Completion (Success)
1. Contractor initiates "Complete Contract" at Destination.
2. System verifies:
   - Fleet is at Destination.
   - Current Time <= Deadline.
   - Fleet has the required Items.
3. **Action**:
   - Items are transferred to Issuer's storage at Destination (or specific target inventory).
   - Reward is paid to Contractor.
   - Collateral is returned to Contractor.
   - Contract status -> `COMPLETED`.

### E. Failure (Default/Loss)
1. If Deadline passes and contract is not completed:
   - Contract status -> `FAILED`.
   - Collateral is transferred to Issuer.
   - Reward (escrowed) is returned to Issuer.
   - Items are considered lost/stolen by Contractor (Contractor keeps them, but lost the collateral). *Alternatively: Items remain with Contractor but they paid the price via collateral.*

## 4. Technical Implementation Details
- **Database**:
  - New tables: `fleets`, `contracts`.
  - Updated table: `inventories` (add `fleet_id` to support mobile inventory).
- **Validation**:
  - Ensure correct locking of funds and items to prevent double-spending or duplication.
