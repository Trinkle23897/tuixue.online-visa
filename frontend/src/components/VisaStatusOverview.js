import React, { useState, useMemo } from "react";
import PropTypes from "prop-types";
import { useSelector } from "react-redux";
import { Collapse, List, Row, Col, Button } from "antd";
import { PlusOutlined, QqOutlined, LineChartOutlined } from "@ant-design/icons";
import { makeOverviewDetailSelector, makeNewestVisaStatusSelector } from "../redux/selectors";

const { Panel } = Collapse;

const overviewPropTypes = {
    overview: PropTypes.shape({
        visaType: PropTypes.string,
        embassyCode: PropTypes.string,
        embassyName: PropTypes.string,
        earliestDate: PropTypes.arrayOf(PropTypes.string),
        latestDate: PropTypes.arrayOf(PropTypes.string),
    }).isRequired,
};

const OverviewNewest = ({ visaType, embassyCode }) => {
    const newestVisaStatueSelector = useMemo(() => makeNewestVisaStatusSelector(visaType, embassyCode), [
        visaType,
        embassyCode,
    ]);
    const newestVisaStatus = useSelector(state => newestVisaStatueSelector(state));
    const { writeTime, availableDate } = newestVisaStatus || { writeTime: ["/"], availableDate: ["/"] };
    return (
        <Col xs={{ span: 24 }} md={{ span: 5 }} style={{ paddingLeft: 8, textAlign: "left" }}>
            {availableDate.join("/")} at {`${writeTime.slice(0, 3).join("/")} ${writeTime.slice(3).join(":")}`}
        </Col>
    );
};
OverviewNewest.propTypes = {
    visaType: PropTypes.string,
    embassyCode: PropTypes.string,
};

// This component can evolve into something VERY COMPLEX with subscription stuff.
// We may want to create a stand-alone component (e.g. OverviewWidget.j) file for it
const OverviewContent = ({ overview, dropdownControl }) => (
    <Row align="middle" justify="space-around">
        <Col xs={{ span: 24 }} md={{ span: 5 }} style={{ paddingLeft: 8, textAlign: "left" }}>
            {overview.embassyName}
        </Col>
        <Col xs={{ span: 24 }} md={{ span: 5 }} style={{ paddingLeft: 8, textAlign: "left" }}>
            {overview.earliestDate.join("/")}
        </Col>
        <Col xs={{ span: 24 }} md={{ span: 5 }} style={{ paddingLeft: 8, textAlign: "left" }}>
            {overview.latestDate.join("/")}
        </Col>
        <OverviewNewest visaType={overview.visaType} embassyCode={overview.embassyCode} />
        <Col md={{ span: 1 }}>
            <Button
                icon={<PlusOutlined />}
                shape="circle"
                size="large"
                onClick={() => console.log(`Click subscription button of ${overview.embassyName}`)}
            />
        </Col>
        <Col md={{ span: 1 }}>
            <Button
                icon={<QqOutlined />}
                shape="circle"
                size="large"
                onClick={() => console.log(`Click QQ button of ${overview.embassyName}`)}
            />
        </Col>
        <Col md={{ span: 1 }}>
            <Button icon={<LineChartOutlined />} shape="circle" size="large" onClick={() => dropdownControl()} />
        </Col>
    </Row>
);
OverviewContent.propTypes = { ...overviewPropTypes, dropdownControl: PropTypes.func };

const VisaStatusOverviewListItem = ({ overview }) => {
    const [panelOpen, setPanelOpen] = useState(false);
    const dropdownControl = () => setPanelOpen(!panelOpen);
    return (
        <List.Item style={{ marginBottom: 12, padding: "24px 12px 0", backgroundColor: "#FFFFFF", borderRadius: 12 }}>
            <OverviewContent overview={overview} dropdownControl={dropdownControl} />
            <Collapse activeKey={panelOpen ? [overview.embassyCode] : []} style={{ width: "100%" }} ghost>
                <Panel key={overview.embassyCode} showArrow={false}>
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
            </Collapse>
        </List.Item>
    );
};
VisaStatusOverviewListItem.propTypes = overviewPropTypes;

export default function VisaStatusOverviewList({ visaType }) {
    const overviewSelector = useMemo(() => makeOverviewDetailSelector(visaType), [visaType]);
    const overviewData = useSelector(state => overviewSelector(state));

    return (
        <List
            itemLayout="vertical"
            dataSource={overviewData}
            renderItem={overview => <VisaStatusOverviewListItem key={overview.embassyCode} overview={overview} />}
        />
    );
}
VisaStatusOverviewList.propTypes = {
    visaType: PropTypes.string.isRequired,
};
