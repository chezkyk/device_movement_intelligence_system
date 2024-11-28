import random
from datetime import datetime, timedelta
import requests
import json
import time


class TestDataGenerator:
    def __init__(self, base_url="http://localhost:5001"):
        self.base_url = base_url
        self.device_ids = [f"D{i:05d}" for i in range(50)]
        self.owner_ids = [f"O{i:05d}" for i in range(30)]  # Less owners than devices
        self.location_ids = [f"L{i:05d}" for i in range(20)]

        # Define some terrorist cells (groups)
        self.terrorist_cells = [
            self.owner_ids[i:i + 5] for i in range(0, 15, 5)
        ]

        # Location patterns for each cell
        self.cell_locations = {
            tuple(cell): random.sample(self.location_ids, 5)
            for cell in self.terrorist_cells
        }

    def generate_normal_movement(self):
        """Generate a regular movement pattern"""
        device_id = random.choice(self.device_ids)
        owner_id = random.choice(self.owner_ids)
        location_id = random.choice(self.location_ids)

        return {
            "device_id": device_id,
            "owner_id": owner_id,
            "timestamp": (datetime.now() - timedelta(
                hours=random.randint(0, 48)
            )).isoformat(),
            "location": {
                "location_id": location_id
            },
            "movement_type": random.choice(["walking", "vehicle"]),
            "confidence_level": round(random.uniform(0.7, 1.0), 2)
        }

    def generate_cell_movement_pattern(self, cell_members):
        """Generate coordinated movements for a terrorist cell"""
        movements = []
        locations = self.cell_locations[tuple(cell_members)]
        base_time = datetime.now() - timedelta(hours=random.randint(0, 48))

        # Assign devices to members
        member_devices = {
            member: random.sample(self.device_ids, random.randint(1, 3))
            for member in cell_members
        }

        # Generate movement pattern through locations
        for i in range(len(locations)):
            current_loc = locations[i]
            next_loc = locations[(i + 1) % len(locations)]

            # Each member moves through locations
            for member in cell_members:
                # Use each of member's devices
                for device in member_devices[member]:
                    # Movement to current location
                    movements.append({
                        "device_id": device,
                        "owner_id": member,
                        "timestamp": (base_time + timedelta(
                            minutes=random.randint(0, 30)
                        )).isoformat(),
                        "location": {"location_id": current_loc},
                        "movement_type": random.choice(["walking", "vehicle"]),
                        "confidence_level": round(random.uniform(0.8, 1.0), 2)
                    })

                    # Movement to next location
                    movements.append({
                        "device_id": device,
                        "owner_id": member,
                        "timestamp": (base_time + timedelta(
                            minutes=random.randint(45, 90)
                        )).isoformat(),
                        "location": {"location_id": next_loc},
                        "movement_type": random.choice(["walking", "vehicle"]),
                        "confidence_level": round(random.uniform(0.8, 1.0), 2)
                    })

            base_time += timedelta(hours=2)

        return movements

    def generate_device_transfer_pattern(self):
        """Generate pattern where devices are transferred between members"""
        movements = []

        # Select random cell and their locations
        cell = random.choice(self.terrorist_cells)
        locations = self.cell_locations[tuple(cell)]

        # Select device to be transferred
        device_id = random.choice(self.device_ids)
        base_time = datetime.now() - timedelta(hours=random.randint(0, 48))

        # Generate transfers between cell members
        for i in range(len(cell)):
            current_owner = cell[i]
            next_owner = cell[(i + 1) % len(cell)]
            transfer_location = random.choice(locations)

            # Current owner's movement to transfer location
            movements.append({
                "device_id": device_id,
                "owner_id": current_owner,
                "timestamp": base_time.isoformat(),
                "location": {"location_id": transfer_location},
                "movement_type": "walking",
                "confidence_level": 0.9
            })

            # Next owner's movement from transfer location
            movements.append({
                "device_id": device_id,
                "owner_id": next_owner,
                "timestamp": (base_time + timedelta(
                    minutes=random.randint(15, 30)
                )).isoformat(),
                "location": {"location_id": transfer_location},
                "movement_type": "walking",
                "confidence_level": 0.9
            })

            base_time += timedelta(hours=3)

        return movements

    def generate_dataset(self):
        """Generate complete test dataset"""
        all_movements = []

        # Generate normal movements
        print("Generating normal movements...")
        for _ in range(1000):
            all_movements.append(self.generate_normal_movement())

        # Generate cell patterns
        print("Generating cell movement patterns...")
        for cell in self.terrorist_cells:
            all_movements.extend(self.generate_cell_movement_pattern(cell))

        # Generate device transfers
        print("Generating device transfer patterns...")
        for _ in range(10):
            all_movements.extend(self.generate_device_transfer_pattern())

        # Sort by timestamp
        all_movements.sort(key=lambda x: x['timestamp'])

        return all_movements

    def send_movements(self, movements, delay=0.1):
        """Send movements to the API"""
        results = []
        total = len(movements)

        print(f"Sending {total} movements to API...")
        for i, movement in enumerate(movements, 1):
            try:
                response = requests.post(
                    f"{self.base_url}/api/v1/movements",
                    json=movement
                )
                results.append({
                    'movement': movement,
                    'status': response.status_code,
                    'response': response.json()
                })

                if i % 100 == 0:
                    print(f"Processed {i}/{total} movements")

                time.sleep(delay)

            except Exception as e:
                print(f"Error sending movement: {str(e)}")
                results.append({
                    'movement': movement,
                    'status': 'error',
                    'error': str(e)
                })

        return results


def main():
    generator = TestDataGenerator()

    print("=== Intelligence System Test Data Generator ===")
    print("\nThis script will generate:")
    print("1. Normal movement patterns")
    print("2. Terrorist cell movement patterns")
    print("3. Device transfer patterns")

    try:
        # Generate data
        movements = generator.generate_dataset()

        # Save to file
        with open('test_movements.json', 'w') as f:
            json.dump(movements, f, indent=2)
        print(f"\nSaved {len(movements)} movements to test_movements.json")

        # Send to API
        if input("\nSend to API? (y/n): ").lower() == 'y':
            results = generator.send_movements(movements)

            # Save results
            with open('test_results.json', 'w') as f:
                json.dump(results, f, indent=2)
            print("\nSaved results to test_results.json")

    except Exception as e:
        print(f"\nError: {str(e)}")


if __name__ == "__main__":
    main()