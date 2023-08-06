# Limpeza geral do produto PyConBrasil

echo "==>> Limpando lixo..."
find ./PyConBrasil/ -name "*.pyc" -exec rm {} \;
find ./PyConBrasil/ -name "*.pyo" -exec rm {} \;
find ./PyConBrasil/ -name "*~" -exec rm {} \;
find ./PyConBrasil/ -name "*.zuml.bak.*" -exec rm {} \;

