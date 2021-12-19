import React from 'react';
import { Button, Modal } from 'react-bootstrap';

declare type ClientRemovalCB = () => void;

type BtClientRemovalModalButtonProps = {
  name: string;
  removeCB: ClientRemovalCB;
};

type BtClientRemovalModalButtonState = {
  show: boolean;
};

export default class BtClientRemovalModalButton extends React.Component<
  BtClientRemovalModalButtonProps,
  BtClientRemovalModalButtonState
> {
  constructor(props: BtClientRemovalModalButtonProps) {
    super(props);

    this.state = {
      show: false,
    };
  }

  handleClose() {
    this.setState({ show: false });
  }

  handleShow() {
    this.setState({ show: true });
  }

  removeClient() {
    const { removeCB } = this.props;
    removeCB();
    this.handleClose();
  }

  render() {
    const { name } = this.props;
    const { show } = this.state;
    return (
      <>
        <Button
          variant="close"
          className="col-1 btn-close-white"
          onClick={() => this.handleShow()}
        />

        <Modal show={show} onHide={() => this.handleClose()}>
          <Modal.Header>
            <Modal.Title>Client Removal</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <p>
              This will remove the client permanently from the KVM. After the
              removal a new bluetooth pairing and trusting needs to perform to
              add the device again to the KVM.
              <br />
              <br />
              Do you really want to remove <strong>{name}</strong>?
            </p>
          </Modal.Body>
          <Modal.Footer>
            <Button
              variant="outline-secondary"
              onClick={() => this.handleClose()}
            >
              Close
            </Button>
            <Button
              variant="outline-danger"
              onClick={() => this.removeClient()}
            >
              Remove
            </Button>
          </Modal.Footer>
        </Modal>
      </>
    );
  }
}
