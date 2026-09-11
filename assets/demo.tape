# VHS tape recording the Cost Cap Tracker demo.
# Install VHS (https://github.com/charmbracelet/vhs) and run:
#   vhs assets/demo.tape
# Requires vhs <= 0.11.0 -- v0.12.0 has a regression where the render step
# receives an already-cancelled context and silently produces no output
# (https://github.com/charmbracelet/vhs/compare/v0.11.0...v0.12.0).
Output assets/demo.gif

Set Shell "bash"
Set FontSize 16
Set Width 1200
Set Height 650
Set Theme "Dracula"
Set TypingSpeed 40ms

Type "mkdir -p /tmp/cost-cap-demo && cd /tmp/cost-cap-demo && rm -f vessel.db"
Enter
Sleep 500ms

Type "alias cost-cap='uv run --project ~/www/cost-cap-tracker cost-cap'"
Enter
Sleep 500ms

Type "cost-cap add --description 'Wind tunnel session' --amount 250000 --category 'Chassis & Aero'"
Enter
Sleep 1s

Type "cost-cap add --description 'Driver salary' --amount 1000000"
Enter
Sleep 1s

Type "cost-cap list"
Enter
Sleep 1500ms

Type "cost-cap summary"
Enter
Sleep 1s

Type "cost-cap set-budget --month $(date +%-m) --cap 100"
Enter
Sleep 1s

Type "cost-cap add --description 'Over the cap' --amount 500 --category 'CapEx'"
Enter
Sleep 2s

Type "cost-cap categories"
Enter
Sleep 1500ms
