import React, { useState } from "react";
import PropTypes from "prop-types";
import { HashLink as Link } from "react-router-hash-link";
import { Row, Col, Button, Layout, Menu, Typography, Popover } from "antd";
import { MenuOutlined, CloseOutlined, EditOutlined } from "@ant-design/icons";
import "./TuixueHeader.less";

const { Header } = Layout;
const { Title } = Typography;

const Logo = () => (
    <Col
        xs={{ span: 2, push: 5 }}
        md={{ span: 2, push: 2 }}
        lg={{ span: 2, push: 3 }}
        xl={{ span: 2, push: 4 }}
        className="logo"
    >
        <img src="https://via.placeholder.com/40" alt="tuixue logo" />
        <Title>Tuixue</Title>
    </Col>
);

const NavMenu = ({ mode, theme, onClick }) => {
    return (
        <Menu theme={theme} mode={mode} onClick={onClick ? () => onClick() : () => {}}>
            <Menu.Item key="visastatus">
                <Link to="/">Visa Status</Link>
            </Menu.Item>
            <Menu.Item key="sysinfo">
                <Link to="/sysinfo">System Status</Link>
            </Menu.Item>
            <Menu.Item key="checkee">
                <a href="https://checkee.info/" target="_blank" rel="noreferrer">
                    Check Reporter
                </a>
            </Menu.Item>
        </Menu>
    );
};
NavMenu.propTypes = {
    mode: PropTypes.oneOf(["vertical", "horizontal", "inline"]),
    theme: PropTypes.oneOf(["dark", "light"]),
    onClick: PropTypes.func,
};

const NavMenuPopover = () => {
    const [menuPop, setMenuPop] = useState(false);

    return (
        <Popover
            content={<NavMenu mode="vertical" theme="light" onClick={() => setMenuPop(!menuPop)} />}
            visible={menuPop}
            overlayStyle={{ minWidth: "65vw" }}
            trigger="click"
            placement="bottomRight"
            arrowPointAtCenter
        >
            <Button
                onClick={() => setMenuPop(!menuPop)}
                size="large"
                icon={menuPop ? <CloseOutlined /> : <MenuOutlined />}
            />
        </Popover>
    );
};

export default function Nav() {
    return (
        <Header className="tuixue-header">
            <Row>
                <Col xs={{ span: 2, push: 1 }} md={0}>
                    <NavMenuPopover />
                </Col>
                <Logo />
                <Col xs={0} md={{ span: 14, push: 6 }}>
                    <NavMenu mode="horizontal" />
                </Col>
                <Col xs={{ span: 2, push: 17 }} md={{ span: 2, push: 5 }} lg={{ span: 2, push: 3 }}>
                    <Button onClick={() => console.log("change")} size="large" icon={<EditOutlined />} />
                </Col>
            </Row>
        </Header>
    );
}
