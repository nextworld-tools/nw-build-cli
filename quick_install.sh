curl -s https://api.github.com/repos/nextworld-tools/nw-build-cli/releases/latest \
| grep "browser_download_url" \
| awk -F'"' '{print $4}' \
| xargs curl -O

sudo chmod +x nwbuild

mv nwbuild /usr/local/bin/nwbuild

nwbuild reset
