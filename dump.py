import os
import struct

def extract_text_with_valid_pointers(pointer_file: str, textdata_file: str, output_txt: str):
    """
    Extrai strings de textdata.dat com base nos ponteiros reais de scenario.dat.
    Inclui o offset de cada string. Ignora ponteiros que apontam para o meio de strings.
    """
    print(f"📥 Lendo ponteiros de: {pointer_file}")
    print(f"📥 Lendo texto de: {textdata_file}")

    try:
        with open(pointer_file, 'rb') as f_ptr:
            pointer_data = f_ptr.read()

        with open(textdata_file, 'rb') as f_txt:
            text_data = f_txt.read()

        # Obter todos os offsets que começam uma string (divididas por \x00\x00)
        valid_string_offsets = set()
        start = 0
        while start < len(text_data):
            end = text_data.find(b'\x00\x00', start)
            if end == -1:
                break
            if end > start:
                valid_string_offsets.add(start)
            start = end + 2  # próxima string

        # Ler ponteiros (4 bytes cada, little endian)
        all_pointers = []
        for i in range(0, len(pointer_data), 4):
            if i + 4 <= len(pointer_data):
                ptr = struct.unpack_from('<I', pointer_data, i)[0]
                if ptr in valid_string_offsets:
                    all_pointers.append(ptr)

        # Remover duplicados e ordenar
        unique_pointers = sorted(set(all_pointers))
        print(f"🔎 {len(unique_pointers)} ponteiros válidos encontrados.")

        with open(output_txt, 'w', encoding='utf-8') as f_out:
            count = 1
            for offset in unique_pointers:
                end = text_data.find(b'\x00\x00', offset)
                if end == -1:
                    continue

                raw_string = text_data[offset:end]
                try:
                    decoded = raw_string.decode('shift_jis').replace('\\n', '\n')
                except UnicodeDecodeError:
                    decoded = "<ERRO NA DECODIFICAÇÃO>"

                if decoded.strip():
                    f_out.write(f"//=========== STRING {count} @0x{offset:X} ===========//\n")
                    f_out.write(decoded + '\n\n')
                    count += 1

        print(f"✅ Extração finalizada: {count - 1} strings salvas em '{output_txt}'.")

    except FileNotFoundError as e:
        print(f"❌ Arquivo não encontrado: {e.filename}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")


# --- Ponto de entrada ---
if __name__ == "__main__":
    input_folder = "input"
    output_folder = "output"

    pointer_file = os.path.join(input_folder, "scenario.dat")
    textdata_file = os.path.join(input_folder, "textdata.dat")
    output_txt = os.path.join(output_folder, "text_with_pointers.txt")

    os.makedirs(output_folder, exist_ok=True)

    extract_text_with_valid_pointers(pointer_file, textdata_file, output_txt)
