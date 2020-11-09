import { createSlice } from "@reduxjs/toolkit";

const latestWrittenSlice = createSlice({
    name: "latestWritten",
    initialState: { filter: [], latestWritten: [] },
    reducers: {
        updateLatestWritten: (state, action) => {
            state.latestWritten.push(...action.payload.latest);
        },
        updateFilter: (state, action) => ({ ...state, filter: action.payload.newFilter }),
    },
});

const { reducer, actions } = latestWrittenSlice;

export const { updateLatestWritten, updateFilter } = actions;

let DUMMY_COUNTER = 0;

export const fetchLatestWritten = () => async (dispatch, getState) => {
    const { latestWritten } = getState();
    const { filter } = latestWritten;

    await new Promise(r => setTimeout(r, 1000));
    console.log(`Current latestWrittent: ${JSON.stringify(latestWritten)}`);
    dispatch(updateLatestWritten({ latest: [DUMMY_COUNTER] }));
    DUMMY_COUNTER += 1;
};

export default reducer;
