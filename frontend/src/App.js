import React, { useEffect } from "react";
import { Provider, useDispatch } from "react-redux";
import store from "./redux";
import { fetchMetadata } from "./redux/metadataSlice";
import Pages from "./pages";
import { NotificationPopUp } from "./components";
import "./assets/styles/index.less";

function App() {
    const dispatch = useDispatch();
    useEffect(() => {
        dispatch(fetchMetadata());
    }, [dispatch]);

    return (
        <>
            <Pages />
            <NotificationPopUp />
        </>
    );
}

export default () => (
    <Provider store={store}>
        <App />
    </Provider>
);
