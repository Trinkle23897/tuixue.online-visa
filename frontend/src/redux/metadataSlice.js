import { createSlice } from "@reduxjs/toolkit";
import { updateFilter } from "./visastatusFilterSlice";
import { getVisaStatusMetadata } from "../services";

const metadataSlice = createSlice({
    name: "metadata",
    initialState: { region: [], embassyLst: [] },
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

    const { embassyLst } = metadata;
    dispatch(updateMetadata({ metadata }));
    Array.from("FBOHL").forEach(visaType => dispatch(updateFilter({ visaType, newFilter: embassyLst.map(e => e[2]) })));

    return Promise.resolve();
};

export default reducer;
