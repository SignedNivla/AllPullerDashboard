# unctad_catalog.py
# Complete UNCTADstat dataset catalog with verified API codes
# Bulk URL: https://unctadstat-api.unctad.org/bulkdownload/{code}/{code_underscore}
# Auth: ClientId + ClientSecret headers

UNCTAD_CATALOG = [

    # INTERNATIONAL TRADE — Trade in Merchandise
    {"group": "International Trade", "subgroup": "Trade in Merchandise", "name": "Merchandise: Total trade and share, annual", "code": "US.TradeMerchTotal"},
    {"group": "International Trade", "subgroup": "Trade in Merchandise", "name": "Merchandise: Total trade growth rates, annual", "code": "US.TradeMerchGR"},
    {"group": "International Trade", "subgroup": "Trade in Merchandise", "name": "Merchandise: Trade balance, annual", "code": "US.TradeMerchBalance"},
    {"group": "International Trade", "subgroup": "Trade in Merchandise", "name": "Volume growth rates of merchandise exports and imports, quarterly", "code": "US.MerchVolumeQuarterly"},
    {"group": "International Trade", "subgroup": "Trade in Merchandise", "name": "Merchandise trade matrix, annual", "code": "US.TradeMatrix"},
    {"group": "International Trade", "subgroup": "Trade in Merchandise", "name": "Merchandise: Intra-trade and extra-trade of country groups by product, annual", "code": "US.IntraTrade"},
    {"group": "International Trade", "subgroup": "Trade in Merchandise", "name": "Merchandise: Terms of trade indices, annual", "code": "US.TermsOfTrade"},
    {"group": "International Trade", "subgroup": "Trade in Merchandise", "name": "Merchandise: Market concentration and structural change indices, annual", "code": "US.ConcentStructIndices"},
    {"group": "International Trade", "subgroup": "Trade in Merchandise", "name": "Import tariff rates on non-agricultural and non-fuel products, annual", "code": "US.Tariff"},
    {"group": "International Trade", "subgroup": "Trade in Merchandise", "name": "Revealed comparative advantage index, annual", "code": "US.RCA"},
    {"group": "International Trade", "subgroup": "Trade in Merchandise", "name": "Merchandise: Product concentration and diversification indices, annual", "code": "US.ConcentDiversIndices"},
    {"group": "International Trade", "subgroup": "Trade in Merchandise", "name": "Merchandise: Theil concentration indices, annual", "code": "US.MerchTheilIndices"},

    # INTERNATIONAL TRADE — Trade in Services
    {"group": "International Trade", "subgroup": "Trade in Services", "name": "Services (BPM6): Preliminary annual estimates based on quarterly data", "code": "US.TradeServCatQuarterlyAnnualized"},
    {"group": "International Trade", "subgroup": "Trade in Services", "name": "Services (BPM6): Trade and growth by main service-category, quarterly", "code": "US.TotAndComServicesQuarterly"},
    {"group": "International Trade", "subgroup": "Trade in Services", "name": "Services (BPM6): Exports and imports by service category, annual", "code": "US.TradeServCatTotal"},
    {"group": "International Trade", "subgroup": "Trade in Services", "name": "Services (BPM6): Exports and imports by service-category and trade-partner, annual", "code": "US.TradeServCatByPartner"},
    {"group": "International Trade", "subgroup": "Trade in Services", "name": "ICT services trade, annual", "code": "US.TradeServICT"},
    {"group": "International Trade", "subgroup": "Trade in Services", "name": "Digitally deliverable services, annual", "code": "US.DigitallyDeliverableServices"},

    # INTERNATIONAL TRADE — Creative Goods and Services
    {"group": "International Trade", "subgroup": "Trade in Creative Goods and Services", "name": "Creative goods: Trade value, annual", "code": "US.CreativeGoodsValue"},
    {"group": "International Trade", "subgroup": "Trade in Creative Goods and Services", "name": "Creative goods: Growth rates, annual", "code": "US.CreativeGoodsGR"},
    {"group": "International Trade", "subgroup": "Trade in Creative Goods and Services", "name": "Creative goods: Index, annual", "code": "US.CreativeGoodsIndex"},
    {"group": "International Trade", "subgroup": "Trade in Creative Goods and Services", "name": "Creative services: Individual totals, annual", "code": "US.CreativeServ_Indiv_Tot"},
    {"group": "International Trade", "subgroup": "Trade in Creative Goods and Services", "name": "Creative services: Group E, annual", "code": "US.CreativeServ_Group_E"},

    # INTERNATIONAL TRADE — Food Trade
    {"group": "International Trade", "subgroup": "Food Trade by Processing Level", "name": "Food trade by category and processing level, annual", "code": "US.TradeFoodCatByProc"},
    {"group": "International Trade", "subgroup": "Food Trade by Processing Level", "name": "Food trade: RCA by processing category, annual", "code": "US.TradeFoodProcCat_Cat_RCA"},
    {"group": "International Trade", "subgroup": "Food Trade by Processing Level", "name": "Food trade by processing category, annual", "code": "US.TradeFoodProcByCat"},
    {"group": "International Trade", "subgroup": "Food Trade by Processing Level", "name": "Food trade: RCA by processing level, annual", "code": "US.TradeFoodProcCat_Proc_RCA"},

    # INTERNATIONAL TRADE — Ocean Economy
    {"group": "International Trade", "subgroup": "Ocean Economy Trade", "name": "Ocean economy trade: Individual economies, annual", "code": "US.OceanTradeIndividualEconomies"},
    {"group": "International Trade", "subgroup": "Ocean Economy Trade", "name": "Ocean economy trade: Regional aggregates, annual", "code": "US.OceanTradeRegionalAggregates"},
    {"group": "International Trade", "subgroup": "Ocean Economy Trade", "name": "Ocean exports per capita: Individual economies, annual", "code": "US.OceanExportsPerCapitaIndividualEconomies"},
    {"group": "International Trade", "subgroup": "Ocean Economy Trade", "name": "Ocean exports per capita: Regional aggregates, annual", "code": "US.OceanExportsPerCapitaRegionalAggregates"},
    {"group": "International Trade", "subgroup": "Ocean Economy Trade", "name": "Ocean RCA: Individual economies, annual", "code": "US.OceanRCAIndividualEconomies"},
    {"group": "International Trade", "subgroup": "Ocean Economy Trade", "name": "Ocean RCA: Regional aggregates, annual", "code": "US.OceanRCARegionalAggregates"},
    {"group": "International Trade", "subgroup": "Ocean Economy Trade", "name": "Ocean Theil indices: Individual economies, annual", "code": "US.OceanTheilIndicesIndividualEconomies"},
    {"group": "International Trade", "subgroup": "Ocean Economy Trade", "name": "Ocean services trade, annual", "code": "US.OceanServices"},

    # INTERNATIONAL TRADE — Biotrade
    {"group": "International Trade", "subgroup": "Biotrade", "name": "Biotrade merchandise, annual", "code": "US.BiotradeMerch"},
    {"group": "International Trade", "subgroup": "Biotrade", "name": "Biotrade merchandise GDP share, annual", "code": "US.BioTradeMerchGDPShare"},
    {"group": "International Trade", "subgroup": "Biotrade", "name": "Biotrade merchandise share, annual", "code": "US.BiotradeMerchShare"},
    {"group": "International Trade", "subgroup": "Biotrade", "name": "Biotrade merchandise RCA, annual", "code": "US.BiotradeMerchRCA"},
    {"group": "International Trade", "subgroup": "Biotrade", "name": "Biotrade merchandise product concentration, annual", "code": "US.BioTradeMerchProdConcent"},
    {"group": "International Trade", "subgroup": "Biotrade", "name": "Biotrade merchandise market indices, annual", "code": "US.BioTradeMerchMarketIndices"},

    # INTERNATIONAL TRADE — Plastics Trade
    {"group": "International Trade", "subgroup": "Plastics Trade", "name": "Plastics trade by partner, annual", "code": "US.PlasticsTradebyPartner"},
    {"group": "International Trade", "subgroup": "Plastics Trade", "name": "Associated plastics trade by partner, annual", "code": "US.AssociatedPlasticsTradebyPartner"},
    {"group": "International Trade", "subgroup": "Plastics Trade", "name": "Hidden plastics trade by partner, annual", "code": "US.HiddenPlasticsTradebyPartner"},
    {"group": "International Trade", "subgroup": "Plastics Trade", "name": "Non-plastic substitutes trade by partner, annual", "code": "US.NonPlasticSubstsTradeByPartner"},

    # ECONOMY, INVESTMENT AND FINANCE — National Accounts
    {"group": "Economy, Investment and Finance", "subgroup": "National Accounts", "name": "GDP: Total and per capita, current and constant prices, annual", "code": "US.GDPTotal"},
    {"group": "Economy, Investment and Finance", "subgroup": "National Accounts", "name": "GDP: Growth rates, annual", "code": "US.GDPGR"},
    {"group": "Economy, Investment and Finance", "subgroup": "National Accounts", "name": "GDP: Expenditure components, annual", "code": "US.GDPComponent"},
    {"group": "Economy, Investment and Finance", "subgroup": "National Accounts", "name": "Gross national income (GNI), annual", "code": "US.GNI"},
    {"group": "Economy, Investment and Finance", "subgroup": "National Accounts", "name": "Goods and services (BPM6), annual", "code": "US.GoodsAndServicesBpm6"},
    {"group": "Economy, Investment and Finance", "subgroup": "National Accounts", "name": "Goods and services balance (BPM6), annual", "code": "US.GoodsAndServBalanceBpm6"},
    {"group": "Economy, Investment and Finance", "subgroup": "National Accounts", "name": "Goods and services trade openness (BPM6), annual", "code": "US.GoodsAndServTradeOpennessBpm6"},
    {"group": "Economy, Investment and Finance", "subgroup": "National Accounts", "name": "Current account balance, annual", "code": "US.CurrAccBalance"},
    {"group": "Economy, Investment and Finance", "subgroup": "National Accounts", "name": "Government expenditures, annual", "code": "US.GovExpenditures"},

    # ECONOMY, INVESTMENT AND FINANCE — Investment and Finance
    {"group": "Economy, Investment and Finance", "subgroup": "Investment and Finance", "name": "FDI inward and outward flows and stock, annual", "code": "US.FdiFlowsStock"},
    {"group": "Economy, Investment and Finance", "subgroup": "Investment and Finance", "name": "Remittances, annual", "code": "US.Remittances"},
    {"group": "Economy, Investment and Finance", "subgroup": "Investment and Finance", "name": "Per capita income (PCI), annual", "code": "US.PCI"},
    {"group": "Economy, Investment and Finance", "subgroup": "Investment and Finance", "name": "Consumer price index (CPI), annual", "code": "US.Cpi_A"},
    {"group": "Economy, Investment and Finance", "subgroup": "Investment and Finance", "name": "Exchange rates crosstab, annual", "code": "US.ExchangeRateCrosstab"},
    {"group": "Economy, Investment and Finance", "subgroup": "Investment and Finance", "name": "Unit value of commodity price index (UCPI), annual", "code": "US.UCPI_A"},
    {"group": "Economy, Investment and Finance", "subgroup": "Investment and Finance", "name": "Unit value of commodity price index (UCPI), monthly", "code": "US.UCPI_M"},

    # COMMODITIES
    {"group": "Commodities", "subgroup": "Commodity Prices", "name": "Commodity price indices, annual", "code": "US.CommodityPriceIndices_A"},
    {"group": "Commodities", "subgroup": "Commodity Prices", "name": "Commodity price indices, monthly", "code": "US.CommodityPriceIndices_M"},
    {"group": "Commodities", "subgroup": "Commodity Prices", "name": "Free market commodity prices, annual", "code": "US.CommodityPrice_A"},
    {"group": "Commodities", "subgroup": "Commodity Prices", "name": "Free market commodity prices, monthly", "code": "US.CommodityPrice_M"},

    # MARITIME TRANSPORT — Merchant Fleet
    {"group": "Maritime Transport", "subgroup": "Merchant Fleet", "name": "Vessel value by ownership, annual", "code": "US.VesselValueByOwnership"},
    {"group": "Maritime Transport", "subgroup": "Merchant Fleet", "name": "Fleet by beneficial owners, annual", "code": "US.FleetBeneficialOwners"},
    {"group": "Maritime Transport", "subgroup": "Merchant Fleet", "name": "Vessel value by registration, annual", "code": "US.VesselValueByRegistration"},
    {"group": "Maritime Transport", "subgroup": "Merchant Fleet", "name": "Merchant fleet by flag of registration and type, annual", "code": "US.MerchantFleet"},
    {"group": "Maritime Transport", "subgroup": "Merchant Fleet", "name": "Seafarers, annual", "code": "US.Seafarers"},
    {"group": "Maritime Transport", "subgroup": "Merchant Fleet", "name": "Ship building, annual", "code": "US.ShipBuilding"},
    {"group": "Maritime Transport", "subgroup": "Merchant Fleet", "name": "Ship scrapping, annual", "code": "US.ShipScrapping"},

    # MARITIME TRANSPORT — Port and Seaborne Trade
    {"group": "Maritime Transport", "subgroup": "Port and Seaborne Trade", "name": "Seaborne trade, annual", "code": "US.SeaborneTrade"},
    {"group": "Maritime Transport", "subgroup": "Port and Seaborne Trade", "name": "Container port throughput, annual", "code": "US.ContPortThroughput"},
    {"group": "Maritime Transport", "subgroup": "Port and Seaborne Trade", "name": "Port calls, annual", "code": "US.PortCalls"},
    {"group": "Maritime Transport", "subgroup": "Port and Seaborne Trade", "name": "Port calls (selected), annual", "code": "US.PortCalls_S"},
    {"group": "Maritime Transport", "subgroup": "Port and Seaborne Trade", "name": "Port calls arrivals, annual", "code": "US.PortCallsArrivals"},
    {"group": "Maritime Transport", "subgroup": "Port and Seaborne Trade", "name": "Port calls arrivals (selected), annual", "code": "US.PortCallsArrivals_S"},

    # MARITIME TRANSPORT — Liner Shipping
    {"group": "Maritime Transport", "subgroup": "Liner Shipping", "name": "Liner shipping connectivity index (LSCI), monthly", "code": "US.LSCI_M"},
    {"group": "Maritime Transport", "subgroup": "Liner Shipping", "name": "Liner shipping connectivity index (LSCI), annual", "code": "US.LSCI"},
    {"group": "Maritime Transport", "subgroup": "Liner Shipping", "name": "Liner shipping bilateral connectivity index (LSBCI), annual", "code": "US.LSBCI"},
    {"group": "Maritime Transport", "subgroup": "Liner Shipping", "name": "Port liner shipping connectivity index (PLSCI), annual", "code": "US.PLSCI"},
    {"group": "Maritime Transport", "subgroup": "Transport Costs", "name": "Maritime transport costs, annual", "code": "US.TransportCosts"},

    # DIGITAL ECONOMY — ICT
    {"group": "Digital Economy", "subgroup": "ICT", "name": "ICT production by sector, annual", "code": "US.IctProductionSector"},
    {"group": "Digital Economy", "subgroup": "ICT", "name": "ICT goods trade value, annual", "code": "US.IctGoodsValue"},
    {"group": "Digital Economy", "subgroup": "ICT", "name": "ICT goods trade share, annual", "code": "US.IctGoodsShare"},
    {"group": "Digital Economy", "subgroup": "ICT", "name": "ICT use by location, annual", "code": "US.IctUseLocation"},
    {"group": "Digital Economy", "subgroup": "ICT", "name": "ICT use by enterprise size, annual", "code": "US.IctUseEnterprSize"},
    {"group": "Digital Economy", "subgroup": "ICT", "name": "ICT use by economic activity (ISIC4), annual", "code": "US.IctUseEconActivity_Isic4"},
    {"group": "Digital Economy", "subgroup": "ICT", "name": "ICT use by economic activity, annual", "code": "US.IctUseEconActivity"},

    # DIGITAL ECONOMY — E-Commerce
    {"group": "Digital Economy", "subgroup": "E-Commerce", "name": "E-commerce total, annual", "code": "US.ECommerceTotal"},
    {"group": "Digital Economy", "subgroup": "E-Commerce", "name": "E-commerce international, annual", "code": "US.ECommerceInternational"},
    {"group": "Digital Economy", "subgroup": "E-Commerce", "name": "Frontiers technology readiness index (FTRI), annual", "code": "US.FTRI"},

    # POPULATION AND LABOUR
    {"group": "Population and Labour", "subgroup": "Population", "name": "Population total, annual", "code": "US.PopTotal"},
    {"group": "Population and Labour", "subgroup": "Population", "name": "Population growth rates, annual", "code": "US.PopGR"},
    {"group": "Population and Labour", "subgroup": "Population", "name": "Population age structure, annual", "code": "US.PopAgeStruct"},
    {"group": "Population and Labour", "subgroup": "Population", "name": "Population dependency ratio, annual", "code": "US.PopDependency"},

    # SUSTAINABLE DEVELOPMENT
    {"group": "Sustainable Development", "subgroup": "Inclusive Growth", "name": "Inclusive growth indicators, annual", "code": "US.InclusiveGrowth"},
    {"group": "Sustainable Development", "subgroup": "Gender", "name": "Gender: Domestic value added, annual", "code": "US.Gender_DomesticValueAdded"},
    {"group": "Sustainable Development", "subgroup": "Gender", "name": "Gender: Tradable industries, annual", "code": "US.Gender_TradableIndustries"},
    {"group": "Sustainable Development", "subgroup": "SDG Indicators", "name": "SDG: Land use, land-use change and forestry (LULFRG), annual", "code": "US.SDG_LULFRG"},
    {"group": "Sustainable Development", "subgroup": "SDG Indicators", "name": "SDG: Portfolio investment (PORFVOL), annual", "code": "US.SDG_PORFVOL"},
]


def get_groups():
    return sorted(set(d["group"] for d in UNCTAD_CATALOG))


def get_datasets(group=None, subgroup=None):
    result = UNCTAD_CATALOG
    if group:
        result = [d for d in result if d["group"] == group]
    if subgroup:
        result = [d for d in result if d["subgroup"] == subgroup]
    return result


def catalog_as_tree():
    """
    Return catalog as tree for render_grouped_multiselect.
    [ { name: group, children: [ { name: subgroup, children: [ { name, id: code } ] } ] } ]
    """
    tree = {}
    for d in UNCTAD_CATALOG:
        g, s = d["group"], d["subgroup"]
        if g not in tree:
            tree[g] = {}
        if s not in tree[g]:
            tree[g][s] = []
        tree[g][s].append({"name": d["name"], "id": d["code"]})

    return [
        {"name": g, "children": [
            {"name": s, "children": ds}
            for s, ds in subgroups.items()
        ]}
        for g, subgroups in tree.items()
    ]