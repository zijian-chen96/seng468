from xml.dom import minidom

def main():
    root = minidom.Document()

    xml = root.createElement('log')
    root.appendChild(xml)

    commandChildren('12121212,abcabc')


    accountTransactionChild = root.createElement('accountTransaction')
    xml.appendChild(accountTransactionChild)

    systemEventChild = root.createElement('systemEvent')
    xml.appendChild(systemEventChild)

    qouteServerChild = root.createElement('qouteServer')
    xml.appendChild(qouteServerChild)

    errorEventChild = root.createElement('errorEvent')
    xml.appendChild(errorEventChild)

    xml_str = root.toprettyxml(indent='\t')

    save_path_file = "testxmlfile.xml"

    with open(save_path_file, "w") as f:
        f.write(xml_str)


def commandChildren(data):
    dataList = data.split(',')

    userCommandChild = root.createElement('userCommand')
    xml.appendChild(userCommandChild)

    timestampChild(data)


def timestampChild(data):
    timestampChild = root.createElement('timestamp')
    timestampChild.appendChild(root.createTextNode(data))
    userCommandChild.appendChild(timestampChild)



if __name__ == '__main__':
    main()
