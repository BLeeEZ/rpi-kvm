class ClientRemovalModalButton extends React.Component {

  constructor(props) {
    super(props)

    this.state = {
      show: false,
    }
  }
  
  handleClose() {
    this.setState({ show: false });
  }

  handleShow() {
    this.setState({ show: true });
  }

  removeClient() {
    this.props.removeCB()
    this.handleClose()
  }
  
  render() {
    return (
      <>
        <button className="btn btn-close btn-close-white col-1" onClick={() => this.handleShow()}></button>

        <ReactBootstrap.Modal show={this.state.show} onHide={() => this.handleClose()}>
          <ReactBootstrap.Modal.Header closeButton>
            <ReactBootstrap.Modal.Title>Client Removal</ReactBootstrap.Modal.Title>
          </ReactBootstrap.Modal.Header>
          <ReactBootstrap.Modal.Body>
            <p>
              This will remove the client permanently from the KVM.
              After the removal a new bluetooth pairing and trusting needs to perform to add the device again to the KVM.
              <br/><br/>
              Do you really want to remove <strong>{this.props.name}</strong>?
            </p>
          </ReactBootstrap.Modal.Body>
          <ReactBootstrap.Modal.Footer>
            <button className="btn btn-outline-secondary" onClick={() => this.handleClose()}>
              Close
            </button>
            <button className="btn btn-outline-danger" onClick={() => this.removeClient()}>
              Remove
            </button>
          </ReactBootstrap.Modal.Footer>
        </ReactBootstrap.Modal>
      </>
    );
  }
}
