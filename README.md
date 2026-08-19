# Cost Cap Tracker

A personal expense tracker themed after F1's cost cap regulations. Log expenses, tag them with F1-flavored categories, set a monthly cost cap, and get a breach warning when you go over it.

Project: https://roadmap.sh/projects/expense-tracker

## Requirements

- Rust (edition 2021) and Cargo

## Build & Run

```bash
make build     # cargo build
make run       # cargo run
make release   # cargo build --release
make check     # cargo check
make test      # cargo test
```

Data is stored locally in a SQLite file (`vessel.db`) created in the working directory on first run.

## Usage

```bash
cargo run -- <COMMAND> [OPTIONS]
```

### Commands

**Add an expense**
```bash
cargo run -- add --description "Wind tunnel session" --amount 250000 --category "Chassis & Aero"
```
`--category` defaults to `General` if omitted.

**Update an expense** (only passed fields change)
```bash
cargo run -- update --id 1 --amount 260000
```

**Delete an expense**
```bash
cargo run -- delete --id 1
```

**List expenses** (optionally filtered by category)
```bash
cargo run -- list
cargo run -- list --category "Personnel"
```

**Show a spending summary** (optionally scoped to a month of the current year)
```bash
cargo run -- summary
cargo run -- summary --month 3
```

**Set a monthly cost cap**
```bash
cargo run -- set-budget --month 3 --cap 500000
```
Adding an expense in a month with a cap set prints how much of the cap is used, or a breach warning if you've gone over.

**Export expenses to CSV**
```bash
cargo run -- export --output expenses.csv
```

**List suggested categories**
```bash
cargo run -- categories
```
