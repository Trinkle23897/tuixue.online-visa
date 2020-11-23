import React, { useState, useMemo } from "react";
import PropTypes from "prop-types";
import { useSelector } from "react-redux";
import { Collapse, Card, List, Row, Col } from "antd";
import { PlusCircleOutlined, UpOutlined, DownOutlined, QqCircleFilled } from "@ant-design/icons";
import { makeOverviewDetailSelector, makeNewestVisaStatusSelector } from "../redux/selectors";

const { Panel } = Collapse;

const OverviewNewest = ({ visaType, embassyName }) => {
    const newestVisaStatueSelector = useMemo(() => makeNewestVisaStatusSelector(visaType, embassyName), [
        visaType,
        embassyName,
    ]);
    const { writeTime, availableDate } = useSelector(state => newestVisaStatueSelector(state));
    return (
        <Col xs={{ span: 24 }} md={{ span: 6 }} style={{ textAlign: "left" }}>
            {availableDate || "/"} at {writeTime}
        </Col>
    );
};
OverviewNewest.propTypes = {
    visaType: PropTypes.string,
    embassyName: PropTypes.string,
};

const OverviewContent = ({ overview }) => (
    <Row align="middle" justify="space-around">
        {/* <Col span={{ xs: 24, md: 6 }} style={{ textAlign: "left" }}>
            {overview.visaType}
        </Col> */}
        <Col xs={{ span: 24 }} md={{ span: 6 }} style={{ textAlign: "left" }}>
            {overview.embassyName}
        </Col>
        <Col xs={{ span: 24 }} md={{ span: 6 }} style={{ textAlign: "left" }}>
            {overview.earliestDate}
        </Col>
        <Col xs={{ span: 24 }} md={{ span: 6 }} style={{ textAlign: "left" }}>
            {overview.latestDate}
        </Col>
        <OverviewNewest visaType={overview.visaType} embassyName={overview.embassyName} />
    </Row>
);
OverviewContent.propTypes = {
    overview: PropTypes.shape({
        visaType: PropTypes.string,
        embassyName: PropTypes.string,
        earliestDate: PropTypes.string,
        latestDate: PropTypes.string,
    }).isRequired,
};

export default function VisaStatusOverviewList({ visaType }) {
    const overviewSelector = useMemo(() => makeOverviewDetailSelector(visaType), [visaType]);
    const overviewData = useSelector(state => overviewSelector(state));

    return (
        <Collapse
            expandIconPosition="right"
            expandIcon={({ isActive }) => (isActive ? <UpOutlined /> : <DownOutlined />)}
            accordion
        >
            {(overviewData || []).map(overview => (
                <Panel header={<OverviewContent overview={overview} />}>
                    <div
                        style={{
                            width: "100%",
                            height: "80px",
                            backgroundColor: "#EFB777",
                            display: "flex",
                            justifyContent: "center",
                            alignItems: "center",
                        }}
                    >
                        <h3> A DOPE ASS plot here</h3>
                    </div>
                </Panel>
            ))}
        </Collapse>
    );
}
VisaStatusOverviewList.propTypes = {
    visaType: PropTypes.string.isRequired,
};
