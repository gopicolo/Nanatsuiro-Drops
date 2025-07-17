import os
import re
import struct

def repack_and_update_pointers(translated_txt_path, original_text_path, original_scenario_path,
                                output_text_path, output_scenario_path):
    print("--- Starting repack and pointer update ---")

    try:
        # --- Read translated texts with offsets ---
        with open(translated_txt_path, 'r', encoding='utf-8') as f:
            content = f.read()

        matches = re.findall(
            r"//=========== STRING (\d+) @0x([0-9A-Fa-f]+) ===========//\n(.*?)\n\n",
            content, re.DOTALL
        )

        if not matches:
            print("❌ No strings with offset found in the translation file.")
            return

        print(f"📥 {len(matches)} text blocks found in .txt")

        # --- Read original binary files ---
        with open(original_text_path, 'rb') as f:
            textdata = bytearray(f.read())

        with open(original_scenario_path, 'rb') as f:
            scenario = bytearray(f.read())

        # --- Get existing pointers (4 bytes each, little endian) ---
        pointer_table = []
        for i in range(0, len(scenario), 4):
            if i + 4 <= len(scenario):
                offset = struct.unpack_from('<I', scenario, i)[0]
                pointer_table.append((i, offset))  # (position_in_file, pointer_value)

        # --- Build map from pointer values to their locations in scenario.dat ---
        pointer_map = {}  # original_offset -> [list of positions in scenario file]
        for pos, ptr in pointer_table:
            pointer_map.setdefault(ptr, []).append(pos)

        # --- Replacement / reinsertion process ---
        used_offsets = set()  # to avoid reusing new space
        textdata_end = len(textdata)

        for str_num, offset_hex, new_text in matches:
            original_offset = int(offset_hex, 16)

            # Encode string
            encoded = new_text.replace('\n', '\\n').encode('shift_jis', errors='ignore') + b'\x00\x00'

            # Find original space end
            end = textdata.find(b'\x00\x00', original_offset)
            if end == -1:
                print(f"⚠️ STRING {str_num}: delimiter \\x00\\x00 not found — skipping.")
                continue
            original_length = (end + 2) - original_offset

            if len(encoded) <= original_length:
                # Fits in original space → overwrite
                textdata[original_offset:original_offset + len(encoded)] = encoded
                print(f"✔️  STRING {str_num} replaced at original offset 0x{original_offset:X}")
            else:
                # Doesn't fit → move to end of file
                new_offset = textdata_end
                textdata += encoded
                textdata_end += len(encoded)
                used_offsets.add(new_offset)
                print(f"🔁 STRING {str_num} relocated: 0x{original_offset:X} → 0x{new_offset:X}")

                # Update all pointers pointing to original_offset
                for ptr_pos in pointer_map.get(original_offset, []):
                    struct.pack_into('<I', scenario, ptr_pos, new_offset)

        # --- Save modified files ---
        os.makedirs(os.path.dirname(output_text_path), exist_ok=True)
        with open(output_text_path, 'wb') as f:
            f.write(textdata)

        with open(output_scenario_path, 'wb') as f:
            f.write(scenario)

        print(f"\n✅ Repack complete.")
        print(f"📦 New textdata.dat: {output_text_path}")
        print(f"📦 New scenario.dat: {output_scenario_path}")

    except Exception as e:
        print(f"❌ Error: {e}")


# --- Main entry ---
if __name__ == "__main__":
    input_folder = "input"
    output_folder = "modified"

    translated_txt = os.path.join("output", "text_with_pointers.txt")
    original_textdata = os.path.join(input_folder, "textdata.dat")
    original_scenario = os.path.join(input_folder, "scenario.dat")

    output_textdata = os.path.join(output_folder, "textdata.dat")
    output_scenario = os.path.join(output_folder, "scenario.dat")

    repack_and_update_pointers(translated_txt, original_textdata, original_scenario,
                                output_textdata, output_scenario)
