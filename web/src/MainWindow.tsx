import React from 'react';
import NavigationBar from './NavigationBar';
import Home from './Home';
import Settings from './Settings';
import BtClients from './BtClients';
import { NotificationProvider, NotificationOutlet } from './Notifications';

type MainWindowState = {
  activeView: string;
};

export default class MainWindow extends React.Component<any, MainWindowState> {
  constructor(props: any) {
    super(props);
    this.state = { activeView: 'Home' };
  }

  switchActiveView(newActiveView: string) {
    this.setState({ activeView: newActiveView });
  }

  renderActiveView() {
    const { activeView } = this.state;
    if (activeView === 'Settings') {
      return <Settings />;
    }
    if (activeView === 'Bt-Clients') {
      return <BtClients />;
    }
    return <Home />;
  }

  render() {
    const { activeView } = this.state;
    return (
      <>
        <header>
          <NavigationBar
            activeView={activeView}
            switchActiveViewCB={(newActiveView) =>
              this.switchActiveView(newActiveView)
            }
          />
        </header>
        <NotificationProvider>
          <NotificationOutlet/>
          <main className="pb-3">{this.renderActiveView()}</main>
        </NotificationProvider>
      </>
    );
  }
}
