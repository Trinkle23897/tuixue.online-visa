import React from "react";
import { Provider } from "react-redux";
import store from "./redux";
import Pages from "./pages";
import { useInitialDataFetch, useWebSocketSubscribe } from "./hooks";
import "./assets/styles/index.less";

function App() {
    useInitialDataFetch();
    useWebSocketSubscribe();

    return <Pages />;
}

export default () => (
    <Provider store={store}>
        <App />
    </Provider>
);
