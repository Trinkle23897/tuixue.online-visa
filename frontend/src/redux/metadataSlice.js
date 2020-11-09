import { createSlice } from "@reduxjs/toolkit";
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
    } catch (e) {
        console.error(`In metadataSlice: ${e}`);
        return;
    }

    const { region, embassy_lst: embassyLst } = metadata;
    dispatch(updateMetadata({ metadata: { region, embassyLst } }));
};

export default reducer;
