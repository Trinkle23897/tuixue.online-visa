import { configureStore } from "@reduxjs/toolkit";
import metadata from "./metadataSlice";
import latestWritten from "./latestWrittenSlice";

export default configureStore({
    reducer: {
        metadata,
        latestWritten,
    },
});
