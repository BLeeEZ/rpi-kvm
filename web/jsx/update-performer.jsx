class UpdatePerformer extends React.Component {
  constructor(props) {
    super(props)

    this.state = {
      isUpdateAvailable: false,
      isUpdateSuccessful: false,
      hasUpdatePerformed: false
    }
  }

  componentDidMount() {
    this.fetchUpdateAvailable();
  }

  fetchUpdateAvailable() {
    fetch(API + 'is_update_available')
      .then(response => response.json())
      .then(
        (result) => {
          this.setState({
            isUpdateAvailable: result.isUpdateAvailable})
        },
        (error) => {
          this.props.notify(NotifyType.error, 'Something went wrong during check for updates...')
        }
      )
  }

  performUpdate() {
    fetch(API + 'perform_update')
      .then(response => response.json())
      .then(
        (result) => {
          this.setState({
            isUpdateSuccessful: result.isUpdateSuccessful,
            hasUpdatePerformed: result.hasUpdatePerformed,
        })
        },
        (error) => {
          this.props.notify(NotifyType.error, 'Something went wrong during trigger RPI-K(V)M update...')
        }
      )
  }

  render() {
    const { isUpdateAvailable, isUpdateSuccessful, hasUpdatePerformed } = this.state;
    if(isUpdateAvailable) {
      let bannerContent = <InfoBanner message="An update is available." />
      let updateButton = ""
      if(hasUpdatePerformed) {
        if(isUpdateSuccessful) {
          bannerContent = <SuccessBanner message="RPI-K(V)M updated successfuly. The update will be active after the next KVM service restart or Raspberry Pi restart." />
        } else {
          bannerContent = <ErrorAlert message="An error occured during RPI-K(V)M update." />
        }
      } else {
        updateButton = 
          <div className="d-grid col-4">
            <button className="btn btn-outline-warning" onClick={() => this.performUpdate()}>
              Perform update
            </button>
          </div>
      }

      return (
        <div className="container">
          <div className="row g-3 align-items-center">
            <h2 className="fw-light">Updates</h2>
            {bannerContent}
            {updateButton}
          </div>
        </div>
      );
    } else {
      return(
        <div className="container">
          <div className="row g-3 align-items-center">
            <h2 className="fw-light">Updates</h2>
            <p>RPI-K(V)M is on latest version.</p>
          </div>
        </div>
      );
    }
  }
}