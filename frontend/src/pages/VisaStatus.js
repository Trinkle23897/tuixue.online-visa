import React, { useEffect, useState, useContext } from "react";
import PropTypes from "prop-types";
import { useDispatch } from "react-redux";
import { Divider, Layout, Typography, List, Card, Button, Collapse, Space } from "antd";
import { PlusCircleOutlined, UpOutlined, DownOutlined, QqCircleFilled } from "@ant-design/icons";
import { TuixueHeader } from "../components";
import "./VisaStatus.less";

const { Content } = Layout;
const { Title } = Typography;
const { Panel } = Collapse;

const OverviewAtom = ({ visaType, embassyName, earliestDt, latestDt }) => {
    return (
        <div className="overview-atom">
            <span>{visaType}</span>
            <span>{embassyName}</span>
            <span>{earliestDt}</span>
            <span>{latestDt}</span>
        </div>
    );
};
OverviewAtom.propTypes = {
    visaType: PropTypes.string.isRequired,
    embassyName: PropTypes.string.isRequired,
    earliestDt: PropTypes.string.isRequired,
    latestDt: PropTypes.string.isRequired,
};

const OverviewCard = ({ date, overview }) => (
    <Card title={<Title level={3}>{date.split("T")[0]}</Title>} className="overview-card">
        {/* <List size="large" dataSource={overview} renderItem={item => <OverviewAtom {...item} />} /> */}
        <Collapse
            expandIconPosition="right"
            expandIcon={({ isActive }) => (isActive ? <UpOutlined /> : <DownOutlined />)}
            ghost
        >
            {overview.map(ov => (
                <Panel
                    header={<OverviewAtom {...ov} />}
                    extra={
                        <>
                            <QqCircleFilled
                                onClick={e => {
                                    alert("Should implement manchanism for adding QQ subscription");
                                    e.stopPropagation();
                                }}
                            />
                            <PlusCircleOutlined
                                onClick={e => {
                                    alert("Should implement mechanism for adding subscription");
                                    e.stopPropagation(); // stop the button from triggering collapase
                                }}
                            />
                        </>
                    }
                >
                    <br />
                    <p style={{ fontSize: "25px", fontWeight: "bold", textAlign: "center" }}>We can add a plot here</p>
                    <br />
                </Panel>
            ))}
        </Collapse>
    </Card>
);
OverviewCard.propTypes = {
    date: PropTypes.string.isRequired,
    overview: PropTypes.array.isRequired,
};

export default function VisaStatus() {
    return (
        <Layout className="tuixue-page">
            <TuixueHeader />
            <Content className="tuixue-content">
                <Title level={2} style={{ textAlign: "center", margin: "8px", padding: "8px" }}>
                    Visa Status Overview
                </Title>
                <List
                    size="large"
                    className="overview-list"
                    itemLayout="horizontal"
                    dataSource={[]}
                    renderItem={item => <OverviewCard {...item} />}
                />
            </Content>
        </Layout>
    );
}
