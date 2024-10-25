# Introduction 

## A wwwpy Project Structure

In a typical **wwwpy** project structure, you'll encounter these three main folders:

- **common:** This folder contains **Python code and resources** that can be shared and executed in both the server and browser environments. Code here should avoid using any server- or browser-specific APIs to ensure compatibility across both. Think of it as a shared library that both environments can access for seamless, environment-neutral functionality.

- **remote:** This folder houses **browser-specific Python code** and resources. At startup, **wwwpy** transfers the contents of both the “common” and “remote” folders to the browser, allowing the code to execute on the client side.

- **server:** This folder is dedicated to **server-side Python code and resources**. The content here stays on the server and is never transferred to the browser.

This structure creates a clear separation of responsibilities, ensuring you can easily distinguish code that should run in the browser from code meant only for the server, while maintaining a flexible shared layer in the **common** folder.

