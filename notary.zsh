#/bin/zsh
codesign --remove-signature diagnosis.app
codesign --force --sign "Developer ID Application: Mei Fu (555AN3VM96)"  --options=runtime --timestamp diagnosis.app
codesign -d -vv "diagnosis.app"
codesign --verify --verbose diagnosis.app

# xcrun notarytool store-credentials "Meifu" --apple-id "mei.fu@umkc.edu" --team-id "555AN3VM96" --password "fqgn-vzni-hnvq-hden"
/usr/bin/ditto -c -k --keepParent "diagnosis.app" "diagnosis.zip"
xcrun notarytool submit diagnosis.zip --keychain-profile "Meifu" --wait
# xcrun notarytool log <id> --keychain-profile "Meifu" developer_log.json