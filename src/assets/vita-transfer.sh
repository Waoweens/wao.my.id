#!/usr/bin/env bash
set -euo pipefail
revision="1.0.0 (2026-01-08)"

# get positional arguments
source_path="${1:-}/picture"
destination_path="${2:-}"

checksum_file="$destination_path/SHA256SUMS"

if [[ -z "$source_path" || -z "$destination_path" ]]; then
	echo "vita-transfer.sh $revision"
	echo "Transfer PlayStation Vita media."
	echo "Open VitaShell, press START, set 'USB device' to 'Memory Card', set 'SELECT button' to 'USB', exit menu, press SELECT, connect Vita via USB."
	echo
	echo "Usage: $0 <source_path> <destination_path>"
	echo "    <source_path>         Path to ux0:"
	echo "    <destination_path>    Path to transfer media to"
	exit 1
fi

if [[ ! -d "$source_path" ]]; then
	echo "Directory '$source_path' does not exist."
	exit 1
fi

mkdir -p "$destination_path"

if [[ ! -f "$checksum_file" ]]; then
	touch "$checksum_file"
fi

mapfile -t -d '' source_files < <(find "$source_path" -type f -printf '%P\0')

for source_file in "${source_files[@]}"; do
	source_file_checksum=$(sha256sum "$source_path/$source_file" | awk '{print $1}')

	stored_checksum=$(grep -F -- "$source_file" "$checksum_file" | awk '{print $1}' || echo "")

	if [[ "$source_file_checksum" != "$stored_checksum" ]]; then
		echo "Transferring '$source_file'..."

		if [[ "$source_file" =~ ^CAMERA.* ]]; then
			destination_file_dir="$destination_path/CAMERA"
		elif [[ "$source_file" =~ ^SCREENSHOT.* ]]; then
			destination_file_dir="$destination_path/SCREENSHOT"
		else
			destination_file_dir="$destination_path/OTHER"
		fi

		mkdir -p "$destination_file_dir"
		cp "$source_path/$source_file" "$destination_file_dir/"

		(
			# cd in to get relative paths
			cd "$source_path"
			sha256sum "$source_file" >> "$checksum_file"
		)

	else
		echo "Skipping '$source_file' (file exists)."
	fi
done