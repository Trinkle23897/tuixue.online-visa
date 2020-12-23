import { createSelector } from "@reduxjs/toolkit";
import { embassyAttributeIdx, findEmbassyAttributeByCode } from "../utils/USEmbassy";

// basic selectors
const metadataSelector = state => state.metadata;
const overviewSelector = state => state.visastatusOverview;
const newestSelector = state => state.visastatusNewest;
const filterSelector = state => state.visastatusFilter;
const embassyLstSelector = createSelector(metadataSelector, metadata => metadata.embassyLst);
export const makeEmbassyBySysSelector = sys =>
    createSelector(embassyLstSelector, embassyLst =>
        sys === "all"
            ? embassyLst.map(emb => emb[embassyAttributeIdx.code])
            : embassyLst.filter(emb => emb[embassyAttributeIdx.sys] === sys).map(emb => emb[embassyAttributeIdx.code]),
    );
const embassyOptionsSelector = createSelector(embassyLstSelector, embassyLst =>
    embassyLst.map(emb => ({ name: emb[embassyAttributeIdx.nameEn], code: emb[embassyAttributeIdx.code] })),
);
const rceTreeSelector = createSelector(metadataSelector, metadata => metadata.regionCountryEmbassyTree);
export const makeEmbassyTreeSelector = sys =>
    createSelector(
        [embassyOptionsSelector, rceTreeSelector, makeEmbassyBySysSelector(sys)],
        (embassyOptions, rceTree, embassyBySys) =>
            rceTree
                .map(({ region, countryEmbassyMap }) => ({
                    region,
                    countries: countryEmbassyMap
                        .map(({ country, embassyCodeLst }) => ({
                            country,
                            cities: embassyOptions
                                .filter(({ code }) => embassyCodeLst.includes(code) && embassyBySys.includes(code))
                                .map(emb => ({ city: emb.code })),
                        }))
                        .filter(countryNode => countryNode.cities.length > 0),
                }))
                .filter(regionNode => regionNode.countries.length > 0),
    );

// generate `make{Some}SelectorByVisaType`
const makeSelectorMakerByVisaType = selector => visType => createSelector(selector, output => output[visType]);

// Selectors by Visa type
const makeOverviewSelectorByVisaType = makeSelectorMakerByVisaType(overviewSelector);
export const makeFilterSelectorByVisaType = makeSelectorMakerByVisaType(filterSelector);

export const makeOverviewDetailSelector = visaType =>
    createSelector(
        [embassyLstSelector, makeOverviewSelectorByVisaType(visaType), makeFilterSelectorByVisaType(visaType)],
        (embLst, overview, filter) =>
            overview
                .filter(ov => filter.includes(ov.embassyCode))
                .map(ov => ({ ...ov, embassyName: findEmbassyAttributeByCode("nameEn", ov.embassyCode, embLst) })),
    );

export const makeNewestVisaStatusSelector = (visaType, embassyCode) =>
    createSelector(newestSelector, newest => newest[visaType][embassyCode]);
