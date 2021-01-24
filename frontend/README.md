# Tuixue frontend

This README helps on setting up the development environment for the frontend React project.

## Node version and installation

> **This project is developed with Node v14.15.0**

[Official NodeJS package installation](https://nodejs.org/en/download/) is okay but it comes with a tiny issue: You will need to `sudo` every `npm install` command as the root directory will be placed under some directory that need the super user access. Plus it will be a pain to clean up your machine. Also you may come to a time when multiple versions of NodeJS need to be installed on your machine, and this brings the need of a version management tool. A VERY popular NodeJS version management tool is [`nvm`](https://github.com/nvm-sh/nvm) (**N**ode **V**ersion **M**anager).

Use `nvm` to install the LTS version of Node:

```sh
nvm install --lts
```

All installed versions of the NodeJS and the Node packages will be placed in `~/.nvm`.

## Set up the development environment

### Install dependencies

Assuming that you are under the `tuixue.online/frontend` directory. Run following command to install the dependencies from `package.json`

```sh
npm install
npm install -D
```

These first commands installs dependencies for React project and the second one install dependencies for development (linting, auto-formatting, etc. Majorly for using the eslint and prettier together with no pain.)

### Create the `.env` file

CRA used .env under the hood to store envrionmental variables. Simply do

```sh
cp .env.default .env
```

### Fire up the server

```sh
npm start
```

or

```sh
yarn start
```

will do.

#### Regarding to `npm` and `yarn`

`npm` and `yarn` are effectively the same, using either of them will be fine. I put `package-lock.json` and `yarn.lock` into .gitignore so it won't cause annoying file change record in git.

## React project folder structure

> This fold strucutre is from my _personal_ experience of best practice in developing a ~~lightweight~~ React project, thus it's opinionated. It provides a decent scalability without too deep a file tree in my opinion.

Here is the current structure of the project:

```sh 
$ tree -L 4 -I node_modules .
.
├── README.md
├── craco.config.js
├── package-lock.json
├── package.json
├── public
│   ├── favicon.ico
│   ├── index.html
│   ├── logo192.png
│   ├── logo512.png
│   ├── manifest.json
│   └── robots.txt
├── src
│   ├── App.js                      # customized
│   ├── App.test.js
│   ├── assets                      # customized
│   │   ├── fonts
│   │   └── styles
│   │       └── index.less
│   ├── components                  # customized
│   │   ├── NotificationPopUp.js
│   │   ├── TuixueHeader.js
│   │   ├── TuixueHeader.less
│   │   └── index.js
│   ├── hooks                       # customized
│   │   └── index.js
│   ├── index.js
│   ├── logo.svg
│   ├── pages                       # customized
│   │   ├── VisaStatus.js
│   │   ├── VisaStatus.less
│   │   └── index.js
│   ├── redux                       # customized
│   │   ├── index.js
│   │   ├── latestWrittenSlice.js
│   │   └── metadataSlice.js
│   ├── reportWebVitals.js
│   ├── services                    # customized
│   │   ├── TuixueAPI.js
│   │   ├── index.js
│   │   └── typeCheck.js
│   └── setupTests.js
└── yarn.lock
```

Folders and file (`App.js`) marked as customized are created for seperation of concerns. Each folder can be considered as a module, `import something from "./folder"` will import the default export of `./folder/index.js`.

`App.js` is initially created by CRA. Here is the entrance of application. _Global context provider like `redux` store and (potentially) ant design customized styles will be provided from this file._ I don't intend to change much of `index.js` unless we are unlocking the `Suspense` experimental feature.

`components` folder stores reusable React components and their corresponding style sheet. It's a good practice to put component and its specific styling in one place for ease of maintaining. Currently style sheets (`Component.less`) and components (`Component.js`) are stored in a flat structure, considering that we don't have a very large amount of components.

`pages` folder play the roles of both construction of the page from components as well as construction of routes for the frontend (using `react-router`'s router components). A "page" is also a React component but it's relatively much larger and contains more complicated logic such as dispatching data fetching as well as manager the layout of a page (visa `antd.Layout` component and its sub-components). Although we only have one page for now, I say we can be reasonalbly ambitious and keep this folder structure for potential scaling in the future ;-)

`redux` folder is where the redux logic implemented. A constructed redux store is exported by default from the top of the module. Both normal actions and async actions (redux-thunk) are exported from the seperated slice files. I'm using the new `@redusjs/toolkit` package which provides a higher level abastraction of the whole redux tech stack. Saving a TONS of time from typing boilerplate code and resulting in a way better code splitting.

`services` folder stores the functions for making AJAX request to backend api. The base
url is store in .env file. We can readily change it when switching to the production server. All of the AJAX logic is implemented using javascript built-in `fetch` API.

`hooks` folder stores the customized hooks. Currently there is only a `index.js` placeholder. We shouldn't custiomized hook until it's too complicated to write in the component file. _Only refactor the hook out when we have to._

`asset` folder stores static file such as font and global style sheet. The font folder is not pushed into the repo yet because it's empty. Styles folder import the antd style sheet for variable overwritten and some classes/mixin/function (to be added) that will be used by other component. Antd component doesn't provide a responsiveness as good as material design, so some customized styling classes will be needed.
