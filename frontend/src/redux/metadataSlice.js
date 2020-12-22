import { createSlice } from "@reduxjs/toolkit";
import { updateFilterAndSetCookie } from "./visastatusFilterSlice";
import { getVisaStatusMetadata } from "../services";
import { getCookie } from "../utils/cookie";

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

    const { defaultFilter } = metadata;
    dispatch(updateMetadata({ metadata }));
    Array.from("FBOHL").forEach(visaType =>
        dispatch(updateFilterAndSetCookie(visaType, getCookie(`filter-${visaType}`, defaultFilter))),
    );

    return Promise.resolve();
};

export default reducer;
