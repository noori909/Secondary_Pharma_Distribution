from logic.rep_logic import add_rep, get_all_reps, set_rep_status
from logic.area_logic import add_area, get_all_areas, set_area_status

# Add reps
add_rep("Ali")
add_rep("Bilal")

# Add areas
add_area("North Zone")
add_area("South Zone")

print("=== REPS ===")
for r in get_all_reps():
    print(r.id, r.name, r.status)

print("=== AREAS ===")
for a in get_all_areas():
    print(a.id, a.name, a.status)

# Deactivate one rep and one area
set_rep_status(1, "inactive")
set_area_status(2, "inactive")

print("\n=== AFTER STATUS CHANGE ===")
for r in get_all_reps():
    print(r.id, r.name, r.status)

for a in get_all_areas():
    print(a.id, a.name, a.status)
