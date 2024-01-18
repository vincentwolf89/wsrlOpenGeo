{
    title: "Ontwerpen met ruimtelijke koppeling",
    content: [
        {
            type: "expression",
            expressionInfo: {
                expression: "              var panden3d = FeatureSetByPortalItem(              Portal('https://www.arcgis.com'),              '686ca5fc6c3f4a638a834c18e9b87b57',              0,              ['*'],              true            );            var portalbomen =  FeatureSetByPortalItem(              Portal('https://www.arcgis.com'),              'fea8ebd688124281afd8f526de77bfc9',              0,              ['*'],              true            );            return {               type: 'text',               text: 'Aantal bomen binnen vlak: '+ Count( Intersects($feature, portalbomen) )            };           "
            }
        }
    ]
}