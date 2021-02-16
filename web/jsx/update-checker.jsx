class UpdateChecker extends React.Component {
  constructor(props) {
    super(props)

    this.state = {
      isUpdateAvailable: false,
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

  render() {
    const { isUpdateAvailable } = this.state;
    if(isUpdateAvailable) {
      return (
        <div className="text-center container">
          <div className="row">
            <div className="alert alert-warning" role="alert">
              <h3 className="fw-light">
                Update available
              </h3>
              <p className="lead">
                An update is possible. Go to settings to perform the update.
              </p>
            </div>
          </div>
        </div>
      );
    } else {
      return(
        <div className="text-center container">
        </div>
      );
    }
  }
}
