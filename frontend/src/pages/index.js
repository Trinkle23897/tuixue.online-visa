import React from "react";
import { BrowserRouter as Router, Switch, Route, Redirect } from "react-router-dom";
import VisaStatus from "./VisaStatus";

export default function Pages() {
    return (
        <Router>
            <Switch>
                <Route path="/" component={() => <VisaStatus />} />
                <Redirect to="/" />
            </Switch>
        </Router>
    );
}
