.PHONY: count test verify table tiny

# Lower and upper bounds for a(1)..a(12) (about 2 seconds).
count:
	uv run a198683 count

# Fast automated tests.
test:
	uv run pytest -q

# Every independent check on the result (about 90 seconds).
verify:
	uv run a198683 verify

# Regenerate tables/a198683_n12.txt (a few seconds).
table:
	uv run a198683 table

# Check a(1)..a(9) with plain Python complex numbers.
tiny:
	uv run a198683 tiny
