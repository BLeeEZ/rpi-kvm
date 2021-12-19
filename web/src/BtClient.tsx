import React from 'react';
import { Button } from 'react-bootstrap';
import { ServerConfig  } from './Common';
import BtClientRemovalModalButton from './BtClientRemovalModalButton';

export type BtClientProps = {
  client: BtClientInfo;
  lastClientOrderNumber: number;
};

export type BtClientInfo = {
  name: string;
  address: string;
  isConnected: boolean;
  order: number;
  isHost: boolean;
};

export class BtClient extends React.Component<BtClientProps, any> {

  setAsActiveBtHost() {
    const { client } = this.props;
    const requestOptions = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ clientAddress: client.address }),
    };

    fetch(
      `${ServerConfig.url}switch_active_bt_host`,
      requestOptions
    );
  }

  changeOrderLower() {
    const { client } = this.props;
    const requestOptions = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        clientAddress: client.address,
        order_type: 'lower',
      }),
    };

    fetch(
      `${ServerConfig.url}change_client_order`,
      requestOptions
    );
  }

  changeOrderHigher() {
    const { client } = this.props;
    const requestOptions = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        clientAddress: client.address,
        order_type: 'higher',
      }),
    };

    fetch(
      `${ServerConfig.url}change_client_order`,
      requestOptions
    );
  }

  removeClient() {
    const { client } = this.props;
    const requestOptions = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ clientAddress: client.address }),
    };

    fetch(`${ServerConfig.url}remove_client`, requestOptions);
  }

  changeConnectState() {
    const { client } = this.props;
    const requestOptions = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ clientAddress: client.address }),
    };
    const connectionApiEndpoint = client.isConnected
      ? 'disconnect_client'
      : 'connect_client';
    fetch(
      `${ServerConfig.url}${connectionApiEndpoint}`,
      requestOptions
    );
  }

  renderSwitchActiveBtHostButton() {
    const { client } = this.props;
    if (client.isHost) return <></>;
    return (
      <Button
        variant="outline-secondary"
        className="mx-1"
        onClick={() => this.setAsActiveBtHost()}
      >
        Set as active Host
      </Button>
    );
  }

  renderOrderLowerButton() {
    const { client } = this.props;
    if (client.order > 0) {
      return (
        <Button
          variant="default"
          className="text-white col-1 py-0 ps-0 pe-3"
          onClick={() => this.changeOrderLower()}
        >
          <i className="bi bi-chevron-left" style={{ fontSize: '0.9rem' }} />
        </Button>
      );
    }
    return (
      <Button
        variant="default"
        className="text-white col-1 py-0 ps-0 pe-3 disabled"
        onClick={() => this.changeOrderLower()}
      >
        <i className="bi bi-chevron-left" style={{ fontSize: '0.9rem' }} />
      </Button>
    );
  }

  renderOrderHigherButton() {
    const { client, lastClientOrderNumber } = this.props;
    if (client.order < lastClientOrderNumber) {
      return (
        <Button
          variant="default"
          className="text-white col-1 py-0 ps-0 pe-3"
          onClick={() => this.changeOrderHigher()}
        >
          <i className="bi bi-chevron-right" style={{ fontSize: '0.9rem' }} />
        </Button>
      );
    }
    return (
      <Button
        variant="default"
        className="text-white col-1 py-0 ps-0 pe-3 disabled"
        onClick={() => this.changeOrderHigher()}
      >
        <i className="bi bi-chevron-right" style={{ fontSize: '0.9rem' }} />
      </Button>
    );
  }

  renderOrderButtons() {
    return (
      <div className="row">
        {this.renderOrderLowerButton()}
        {this.renderOrderHigherButton()}
      </div>
    );
  }

  renderConnectedCard() {
    const { client } = this.props;
    const isHostContent = client.isHost ? '(active Host)' : '';

    return (
      <div className="col-md-6 ">
        <div className="card mb-3 border-success">
          <div className="card-header bg-success pb-0">
            <div className="row">
              <div className="text-center text-white col-2">
                {this.renderOrderButtons()}
              </div>
              <h5 className="text-center text-white col-8">{client.name}</h5>
            </div>
          </div>
          <div className="card-body">
            <h6 className="card-title">Connected {isHostContent}</h6>
            <p className="card-text">{client.address}</p>
            <div className="text-end">
              {this.renderSwitchActiveBtHostButton()}
              <Button
                variant="outline-danger"
                onClick={() => this.changeConnectState()}
              >
                Disconnect
              </Button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  renderDisconnectedCard() {
    const { client } = this.props;
    return (
      <div className="col-md-6 ">
        <div className="card mb-3 border-secondary">
          <div className="card-header bg-secondary pb-0">
            <div className="row">
              <div className="text-center text-white col-2">
                {this.renderOrderButtons()}
              </div>
              <h5 className="text-center text-white col-8">{client.name}</h5>
              <div className="text-center text-white col-1 offset-1">
                <BtClientRemovalModalButton
                  name={client.name}
                  removeCB={() => this.removeClient()}
                />
              </div>
            </div>
          </div>
          <div className="card-body">
            <h6 className="card-title">Disconnected</h6>
            <p className="card-text">{client.address}</p>
            <div className="text-end">
              {this.renderSwitchActiveBtHostButton()}
              <Button
                variant="outline-success"
                onClick={() => this.changeConnectState()}
              >
                Connect
              </Button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  render() {
    const { client } = this.props;
    if (client.isConnected) {
      return this.renderConnectedCard();
    }
    return this.renderDisconnectedCard();
  }
}
