# Geracao do codigo do produto PyConBrasil
# Invocar este script do mesmo nivel do diretorio ./PyConBrasil

./PyConBrasil/model/clean_trash.sh

python2.4 ArchGenXML/ArchGenXML.py -c PyConBrasil/model/generate.conf PyConBrasil/model/PyConBrasil.zuml

