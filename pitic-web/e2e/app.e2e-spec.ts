import { PiticWebPage } from './app.po';

describe('pitic-web App', () => {
  let page: PiticWebPage;

  beforeEach(() => {
    page = new PiticWebPage();
  });

  it('should display welcome message', () => {
    page.navigateTo();
    expect(page.getParagraphText()).toEqual('Welcome to app!!');
  });
});
