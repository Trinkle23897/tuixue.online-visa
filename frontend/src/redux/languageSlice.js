import { createSlice } from "@reduxjs/toolkit";
import { setCookie } from "../utils/cookie";
import i18n from "../utils/i18n";

const languageSlice = createSlice({
    name: "language",
    initialState: i18n.language,
    reducers: {
        updateLanguage: (state, action) => {
            return action.payload.language;
        },
    },
});

const { reducer, actions } = languageSlice;
export const { updateLanguage } = actions;

export default reducer;
