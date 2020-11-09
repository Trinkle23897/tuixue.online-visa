import React from "react";
import { Layout, Menu, Typography } from "antd";
import "./TuixueHeader.less";

const { Header } = Layout;
const { Title, Text } = Typography;

const Logo = () => {
    return (
        <div className="logo">
            <img src="https://via.placeholder.com/40" alt="tuixue logo" />
            <Title>Tuixue</Title>
        </div>
    );
};

export default function Nav() {
    return (
        <Header className="tuixue-header">
            <Logo />
            {/* <Title style={{ color: "white" }}>Tuixue</Title> */}
        </Header>
    );
}
