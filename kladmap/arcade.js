return {
    type: 'fields',
    title: 'Algemeen',
    //description : '',
    fieldInfos: [{
        fieldName: "UittredepuntenID",
    },
    {
        fieldName: "Scenariotype"
    },
    {
        fieldName: "Scenariokans op vakniveau"
    },

    ],
    attributes: { 
        'UittredepuntenID': Round($feature.UittredepuntenID, 0), 
        'Scenariotype': $feature.Scenariotype, 
        'Scenariokans op vakniveau': Round($feature.Scenariokans_op_vakniveau, 2) 
    }

}

return {
    type: 'fields',
    title: 'Berekening aanwezig verval',
    //description : '',
    fieldInfos: [{
        fieldName: "Verval [m]",
    },
    {
        fieldName: "VW dikte deklaag [m]"
    },
    {
        fieldName: "Verval - 0.3d [m]"
    },

    ],
    attributes: { 
        'Verval [m]': Round($feature.Verval__m_, 2), 
        'VW dikte deklaag [m]': Round($feature.VW_dikte_deklaag__m_, 2), 
        'Verval - 0.3d [m]': Round($feature.Verval___0_3d__m_, 2) 
    }

}

return {
    type: 'fields',
    title: 'Invoer Sellmeijer',
    //description : '',
    fieldInfos: [{
        fieldName: "VW dikte watervoerendpakket [m]",
    },
    {
        fieldName: "VW kh watervoerendpakket [m/dag]"
    },
    {
        fieldName: "VW kD-waarde watervoerendpakket [m2/dag]"
    },
    {
        fieldName: "VC korrelgrootte d70 [m]"
    },
    {
        fieldName: "Effectieve kwelweglengte [m]"
    },

    ],
    attributes: { 
        'VW dikte watervoerendpakket [m]': Round($feature.VW_dikte_watervoerendpakket__m_, 2), 
        'VW kh watervoerendpakket [m/dag]': Round($feature.VW_kh_watervoerendpakket__m_dag_, 2), 
        'VW kD-waarde watervoerendpakket [m2/dag]': Round($feature.VW_kD_waarde_watervoerendpakket__m2_dag_, 2),
        'VW korrelgrootte d70 [m]': Round($feature.VC_korrelgrootte_d70__m_, 2),
        'Effectieve kwelweglengte [m]': Round($feature.Effectieve_kwelweglengte__m_, 2),
    }

}


return {
    type: 'fields',
    title: 'Invoer opbarsten',
    //description : '',
    fieldInfos: [{
        fieldName: "VW volumegewicht deklaag [kN/m3]",
    },
    {
        fieldName: "VW stijghoogte [m NAP]"
    },

    ],
    attributes: { 
        'VW volumegewicht deklaag [kN/m3]': Round($feature.VW_volumegewicht_deklaag__kN_m3_, 2), 
        'VW stijghoogte [m NAP]': Round($feature.VW_stijghoogte__m_NAP_, 2), 
    }

}

return {
    type: 'fields',
    title: 'Resultaat opbarsten',
    //description : '',
    fieldInfos: [{
        fieldName: "Stabiliteitsfactor opbarsten zonder veiligheidsfactoren [-]",
    },
    {
        fieldName: "Betrouwbaarheidsindex opbarsten [-]"
    },

    ],
    attributes: { 
        'Stabiliteitsfactor opbarsten zonder veiligheidsfactoren [-]': Round($feature.Stabiliteitsfactor_opbarsten_zonder_veiligheidsfactoren____, 2), 
        'Betrouwbaarheidsindex opbarsten [-]': Round($feature.Betrouwbaarheidsindex_opbarsten____, 2), 
    }

}

return {
        type: 'fields',
        title: 'Resultaat heave',
        //description : '',
        fieldInfos: [{
            fieldName: "Stabiliteitsfactor heave zonder veiligheidsfactoren [-]",
        },
        {
            fieldName: "Betrouwbaarheidsindex heave [-]"
        },
    
        ],
        attributes: { 
            'Stabiliteitsfactor heave zonder veiligheidsfactoren [-]': Round($feature.Stabiliteitsfactor_heave_zonder_veiligheidsfactoren____, 2), 
            'Betrouwbaarheidsindex heave [-]': Round($feature.Betrouwbaarheidsindex_heave____, 2), 
        }
    
    }

return {
        type: 'fields',
        title: 'Resultaat piping',
        //description : '',
        fieldInfos: [{
            fieldName: "Kritiek verval piping [m]",
        },
        {
            fieldName: "Stabiliteitsfactor piping zonder veiligheidsfactoren [-]"
        },
        {
            fieldName: "Betrouwbaarheidsindex piping [-]"
        },
    
        ],
        attributes: { 
            'Kritiek verval piping [m]': Round($feature.Kritiek_verval_piping__m_, 2), 
            'Stabiliteitsfactor piping zonder veiligheidsfactoren [-]': Round($feature.Stabiliteitsfactor_piping_zonder_veiligheidsfactoren____, 2), 
            'Betrouwbaarheidsindex piping [-]': Round($feature.Betrouwbaarheidsindex_piping____, 2), 
        }
    
    }


    return {
        type: 'fields',
        title: 'Resultaten',
        //description : '',
        fieldInfos: [{
            fieldName: "UittredepuntenID",
        },
        {
            fieldName: "Urgentie probabilistisch"
        },
    
        ],
        attributes: { 
            'UittredepuntenID': Round($feature.UittredepuntenID, 0), 
            'Urgentie probabilistisch': $feature.Urgentie_prob, 
        }
    
    }





