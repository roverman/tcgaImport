mkdir -p /mnt/out
cd /home/ubuntu/tcgaImport
python tcgaImport.py build -u data/tcga_uuid_map -w /mnt/workdir -m /mnt/mirror --checksum-delete --download --outdir /mnt/out ${basename}
python synapseLoad_files.py --project syn3049890 --push /mnt/out/
