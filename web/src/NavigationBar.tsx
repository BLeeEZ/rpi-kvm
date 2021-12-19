/* eslint-disable jsx-a11y/anchor-is-valid */
import React from 'react';
import { Navbar, Nav } from 'react-bootstrap';

declare type SwitchActiveViewCB = (activeView: string) => void;

type NavbarProps = {
  activeView: string;
  switchActiveViewCB: SwitchActiveViewCB;
};

export default class NavigationBar extends React.Component<NavbarProps, any> {
  onSelect(selectedKey: string | null) {
    const { switchActiveViewCB } = this.props;
    if (selectedKey) switchActiveViewCB(selectedKey);
  }

  render() {
    const { activeView } = this.props;
    return (
      <>
        <Navbar bg="dark" variant="dark" className="navbar-expand px-3">
          <a className="navbar-brand" href="#">RPI-K(V)M</a>
          <Nav
            className="me-auto"
            activeKey={activeView}
            onSelect={(selectedKey) => this.onSelect(selectedKey)}
          >
            <Nav.Link eventKey="Home">Home</Nav.Link>
            <Nav.Link eventKey="Bt-Clients" className="me-auto">
              Bt-Clients
            </Nav.Link>
          </Nav>
          <Nav
            activeKey={activeView}
            onSelect={(selectedKey) => this.onSelect(selectedKey)}
          >
            <Nav.Link eventKey="Settings" className="py-0">
              <i className="bi bi-gear-fill fs-3" />
            </Nav.Link>
          </Nav>
        </Navbar>
      </>
    );
  }
}
