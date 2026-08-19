.PHONY: run check build release

run:
	cargo run

check:
	cargo check

build:
	cargo build

release:
	cargo build --release

test:
	cargo test
