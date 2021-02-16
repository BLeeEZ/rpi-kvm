class MainView extends React.Component {
  constructor(props) {
    super(props)
  }

  render() {
    return (
      <section id="main">
        <UpdateChecker notify={this.props.notify} />
        <WelcomeBanner name="Raspberry Pi K(V)M" message="Manage your connected bluetooth clients" />
        <BtClients notify={this.props.notify}/>
      </section>
    );
  }
}
