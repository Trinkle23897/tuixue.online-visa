import { createSlice } from "@reduxjs/toolkit";
import { updateFilter } from "./visastatusFilterSlice";
import { getVisaStatusMetadata } from "../services";
import { embassyAttributeIdx } from "../utils/USEmbassy";
import { getCookie } from "../utils/cookie";
import i18n, { namespace, lngs, countries } from "../utils/i18n";

const metadataSlice = createSlice({
    name: "metadata",
    initialState: { region: [], regionCountryEmbassyTree: [], embassyLst: [], visaTypeDetails: {}, defaultFilter: [] },
    reducers: {
        updateMetadata: (state, action) => action.payload.metadata,
    },
});

const { reducer, actions } = metadataSlice;

export const { updateMetadata } = actions;

export const fetchMetadata = () => async dispatch => {
    let metadata;
    try {
        metadata = await getVisaStatusMetadata();
        if (!metadata) {
            // we could dispatch an error message to update redux and re-render UI
            // For now just handle any problem silently
            return Promise.resolve();
        }
    } catch (e) {
        console.error(`In metadataSlice: ${e}`);
    }

    const { defaultFilter, embassyLst } = metadata;
    dispatch(updateMetadata({ metadata }));
    Array.from("FBOHL").forEach(visaType =>
        dispatch(updateFilter({ visaType, newFilter: getCookie(`filter-${visaType}`, defaultFilter) })),
    ); // no need to set cookie here

    // programatically add i18n resource
    const embassyNameEn = Object.fromEntries(
        embassyLst.map(emb => [emb[embassyAttributeIdx.code], emb[embassyAttributeIdx.nameEn]]),
    );
    const embassyNameCn = Object.fromEntries(
        embassyLst.map(emb => [emb[embassyAttributeIdx.code], emb[embassyAttributeIdx.nameCn]]),
    );

    const countryCodes = Array.from(new Set(embassyLst.map(emb => emb[embassyAttributeIdx.country])));
    const countryNameEn = Object.fromEntries(
        countryCodes.map(countryCode => [countryCode, countries.getName(countryCode, lngs.en, { select: "official" })]),
    );
    const countryNameCn = Object.fromEntries(
        countryCodes.map(countryCode => [countryCode, countries.getName(countryCode, lngs.zh, { select: "official" })]),
    );

    i18n.addResources(lngs.en, namespace, { ...countryNameEn, ...embassyNameEn });
    i18n.addResources(lngs.zh, namespace, { ...countryNameCn, ...embassyNameCn });
    i18n.changeLanguage(i18n.language);

    return Promise.resolve();
};

export default reducer;
