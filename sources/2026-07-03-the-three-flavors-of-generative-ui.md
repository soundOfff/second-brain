---
id: 2026-07-03-the-three-flavors-of-generative-ui
title: "The Three Flavors of Generative UI — Tyler Slaton, CopilotKit"
type: transcript
url: https://www.youtube.com/watch?v=a-K_qFUmda0
author: Mastra
captured: 2026-07-03
---

Hey everyone, my name is Tyler. I'm from the CopilotKit team — I'm part of the founding team there, and I've been there for about a year and a half. I joined because I was really excited about agentic experiences and how we can optimize the UX for users who are utilizing the agents we built.

So today I really want to talk about generative UI. I'll talk a little bit about CopilotKit, the state of agentic UI today, what AG-UI is — our agent-agnostic protocol — and then we'll get into some cool generative UI demos. We'll also talk a little bit about what we see on the horizon here at CopilotKit.

As we go through this, I think this is kind of cool — I actually live-coded all of these slides, so I have CopilotKit embedded in this application. I can ask it to say hi to everyone, and it's actually embedded into our application, so pretty cool. We're going to be doing a lot of cool stuff with these slides. I'm pretty stoked about it.

So what is CopilotKit? CopilotKit is the framework for building AI copilots, which we define as user-facing agentic applications. We're open source, and we're at 30,000 GitHub stars. Our protocol, AG-UI, just hit 12,000 stars, and it grows every day. We also power 15 million agent interactions per month — that's basically a user saying hi to an agent, or a user generating some UI. We're powering about 15 million of those a month. We work with Fortune 100s, unicorns, startups, really everyone in between — we're actually used by 10% of the Fortune 500. Again, we're the company behind the AG-UI protocol, which we'll talk about a little bit.

So I want to talk about the state of agentic UI before we get into generative UI, because I feel like that's a really nice backdrop for us to consider all these cool patterns we're going to be talking about.

At CopilotKit we've existed since ChatGPT 3.5, and we've seen a lot of interesting developments in the agent experience space — we've actually existed since before agents existed. The different paradigms people use to make agents seem faster and more responsive, and to give them steering, has really evolved over time. But one thing that has really persisted is that people are trying to do two core things when they build agentic applications.

One is optimizing their SaaS and making it easier to navigate — a SaaS copilot. Who here uses Linear? Yeah, a bunch of people. Linear has a copilot now; we're going to look at that in a second. Linear is planning software, if you've never used it — you can ask it to go create a bunch of tickets for you, you can ask it about the status of some project, and it's able to answer you.

On the other end of that is productivity copilots — this is Claude Code. Who here is a Claude Code user? Codex? Yeah, I've been told Codex is really on the upswing — I've been trying out Codex lately, but Claude Code is my daily driver. This is where you're doing your core work, where you're building — this is actually where I built all of my slides today. It's just a Vite application where I set up a bunch of HTML and embedded CopilotKit on top of it.

But there's really one challenge we've seen everyone facing: agentic applications are really complex. There's a lot of complexity to them, and one piece of that is that they break the traditional request-and-response paradigm we're used to. For one thing, they're very long-running.

We need to optimize for that long-running nature through a couple of different mechanisms. One is that models stream, so they seem faster than they really are — if a task takes five minutes but you get the output as it's progressing, you can steer it: you can interrupt it and say, "Hey, you're going down the wrong path," or it just seems faster because you're actually seeing responses. They're also structured and unstructured — they can come in as structured JSON outputs, or through markdown, or just text. And, as we'll see today, they can come in through UI as well, which is quite interesting. They also involve a lot of handoff of control — you can delegate to sub-agents, and those sub-agents are parallelized and need to report back status, and there's a lot of complexity involved with that, which is even more complex when you need to show that status to a user.

And as we'll see today, they can also provide non-deterministic UIs — that's actually a lot of what this talk is focused on.

So what can we do to ship applications at scale easily, and just think about our business logic? That's why we built AG-UI — the Agent User Interaction protocol for connecting agentic backends and agentic frontends.

As we see it, it's the protocol that completes the full spectrum of input between a user and an agent. MCP is for tools, for context, for resources like files that give context to an agent — and, as we'll talk about today, it can now return UI as well, so MCP servers can embed applications into super-hosts like ChatGPT or Claude. A2A is for two agents to communicate, which allows you to create agent meshes — this is what brings up that delegation of sub-agents, letting you create meshes of agents that all plug together.

AG-UI, we want it to be the exact same thing as A2A, but for users — meeting your users where they are. Right now CopilotKit is the React client, but we also have an Angular client, and we have the capacity to send events to Rust, to Go, to anywhere you write a program. We're also currently building out Slack integrations and things like that, so you can actually interact with users where they are.

The way AG-UI actually works is it's a client-server architecture, where the client is your application, where your users are, and the server is your agent. For example, we might have a backend with a master agent, and that master agent emits events to us, and those events are sent as AG-UI events. This is a streaming-based protocol.

It's a little small, so I'll zoom in here. This example stream has a "run started" event that says what run or turn we're on, as well as what group of this interaction we're on — that's the thread ID. Then a text message starts: it has a role, just like you're used to, it has an ID — a lot of this starts to look familiar. It has the actual content, which is the deltas. It's a streaming-based protocol, so it's built for efficient transfer of data — you just get the deltas as opposed to everything all at once. Then we get a text-message-end event and a run-finished event. This is actually what all of the generative UI I'm going to show you today is built on top of.

There are events for tool calling, and there are what we call activity events, which are basically messages that shouldn't be part of the state but are just updates to the user. This is how we transfer things like A2UI, which I'll talk about today, MCP apps, and a bunch of other really interesting things.

But if you take one thing away: CopilotKit is the React consumer of AG-UI events. Everything I'm showing you today — this little copilot on the side here — is connected to a master agent.

So let's talk about generative UI. Generative UI, as we see it, has a spectrum, and that spectrum has three buckets — it's really a dial between control and flexibility, and as we move forward, that dial moves from control to flexibility.

On the left-hand side, CopilotKit ships with this concept of useComponent, where you can take a component from your frontend, give it to your agent, and now your agent is able to use and show that component to your user.

In the middle, we'll talk about declarative UI — this is where you have a schema that maps to a renderer, and CopilotKit takes care of all the interactions on the frontend and transmits those events back to the agent via AG-UI. This includes things like JSON Render — we also have our own approach called Hash Brown.

And finally we'll talk about MCP apps, which are closer to the more-flexibility end. For example, Excalidraw has a great use case where you can generate Excalidraw boards, and the agent is able to control every single pixel on that board — it's really flexible, but you can get some really wild things out of it.

We actually just released a new feature yesterday — if you haven't used CopilotKit before, try the latest version. It's called open generative UI, and it allows the agent to securely render raw HTML into your application, so you can get throwaway pieces of software connected right into your data.

So let's talk about controlled generative UI — this is actually an embedded application, and it's why I live-coded all my slides. Controlled generative UI is where you take some chart components and give them to the agent. This chart is one example — you can take any component in your entire component library, give it to the agent, and the agent is able to infer the props, which maps to tool-call args, which maps to streaming. So we get this whole component streamed in real time, and it looks quite consistent with our design system, because I wrote that component for this presentation.

It gives you really deep control over the UI the agent generates, because you're just providing React components, and the agent builds up the inputs and reads the outputs. These are built on top of tool calls, and sometimes also on top of agent state — we'll see a canvas-style application at the end that's built on top of working memory inside of Mastra.

Let's look at the code a little bit — I'll make this larger so we can all see it. First, we define a Mastra agent on the left, a simple one we call the data agent. It has a tool that's able to get some data from the backend. I simplified this down — the actual data I'm pulling in the demo I just showed you is from a CSV, but imagine we have data returned from a database, structured in some way. Then, through AG-UI, we transfer that to the frontend. I define a component called PieChart, and tell it that this component displays a pie chart — this is how the agent knows how to use a component I've defined. On the right-hand side here we're on CopilotKit's frontend; on the left side is the Mastra backend.

Then I define a Zod schema — these are the parameters the agent can provide. Finally, in the render, I pass a component called PieChart, which is just a React component, and it takes that Zod schema and puts it into the PieChart component, so we get that really nice UI.

The pros of this are that it's really simple to write — we write a component, give it to our agent, and the agent can show UI based on our data. It keeps your designers happy, because you get pixel-perfect accuracy and pixel-perfect UX. It's great for the common paths in your application — if you want something to always act the same way, but have the agent utilize it, controlled generative UI is perfect for that.

Some of the cons, though: it's high coupling between the backend and the frontend — you need to make the agent aware of these tools. And the codebase grows linearly as you add new use cases, because you have to add a tool per component in this approach. So if you have 25 components you want the agent to use, you now have 25 tools, and that's a lot of context — it ends up polluting the context window.

I want to move on to declarative generative UI, which solves a lot of those problems. The backdrop here is that we're using Google's declarative generative UI spec, A2UI. It's a semi-open approach to generative UI, where you have constrained UIs driven by a declarative spec that map to renderers on the frontend and can be interacted with by the user.

It's kind of in between static and open-ended — static is that control we were just talking about, and open-ended we'll talk about next. It's typically described through cards and widgets with recurring elements embedded within them, so the agent is delegating layout, but the components are predetermined.

For example, I have a component for my agent that generates a card that can embed flight data inside it — I gave it some logos, and it composes all of these together, and I get this UI at the end. These UIs are all interactable, so I can select my Delta Airlines flight, and it responds back that I did that. So this is declarative generative UI.

If we look at the agent code, we have a flights agent, and that flights agent says, "Here are the components I can give you when you call that tool." We create a tool, and we create a surface in A2UI — this is basically like a component — and then we provide updates that component can carry. For example, I can update the data model, which then maps to these flight cards.

On the CopilotKit side, we build a catalog out of those components — we can share types between them because Mastra is TypeScript. We have a parameter in our CopilotKit provider for taking A2UI catalogs. So basically, you define a schema — that's what's on the left side here with this search-flights tool — and that gets bound to the Mastra agent. The Mastra agent decides to call it, sends the schema to the frontend, and the schema renders and hydrates into an interactive component.

So, some pros and cons: now we have lower coupling between the backend and the frontend. It can accommodate many of your core use cases as well, and it's great for the long tail of user interactions in your application. You can give it a suite of components, and the agent delegates to sub-agents to generate that schema, so now you only have one tool to generate UIs, as opposed to 20.

And it's really extensible to basically any rendering framework, because it's just a JSON schema. The con, though, is that the LLM is now controlling the layout, so the layout can vary between demos — the demo I gave you earlier can vary minutely, but it varies every single time, because it's generating the JSON on the fly and showing it back to you. As a result, it can vary pretty unpredictably.

All right, last one is kind of the wild west — this is the new feature I just mentioned, open generative UI. I have this button here that's going to take a second to run because it's generating a bunch of HTML, but it's going to embed an iframe into our application — actually a double iframe, for security. Then it's going to show you raw HTML rendering up in our chat here, and we'll be able to interact with this calculator component. This changes literally every single time — it looks different so often — but pretty consistently it does work, which is kind of cool. Two plus two is four, good job.

This is where the agent is basically saying, "I'm going to give you whatever you want." With CopilotKit, we can get a bunch of context from the Mastra agents, and then generate a fully interactable UI that the agent spins up on the fly and shows to the user. This is just rendering raw HTML inside an iframe. CopilotKit sends a client tool through AG-UI — AG-UI, as a protocol, has a way to send tools from the frontend to your agents, and the agent is able to execute that. That's actually what's happening here: we're giving the agent the ability to write some HTML.

Let's take a look at how that actually works. I just have a really simple Mastra agent on the left, and on the right I just turn on open generative UI. CopilotKit takes care of the rest, and voilà — now I can generate basically any UI the user might want, inside my chat application.

This is rendered right inside the chat. We also have a bunch of headless UI primitives, which let us take that agent-generated UI and put it into our application wherever we want.

So now we have really low coupling between the backend and the frontend — the backend only gets one tool. The backend can say, "Generate all the HTML, here it is," and the frontend renders it. That can be literally anything, and it can all be grounded in your data, which is really cool — you can create disposable pieces of interface just to show your user some data, without ever having to define it yourself.

But it can vary very unpredictably, and it's difficult to style — I told it to do neo-brutalist, and it looked kind of bad that time. If I did it ten other times, it would look good sometimes and bad other times. And you have to do this double-iframe thing, so that it isn't able to hijack a user session.

All right, last thing I want to talk about is agent state. Who here has used Mastra? Hopefully a lot. Mastra has this working-memory concept, which is structured pieces of data that you can manipulate as a Mastra agent runs, and CopilotKit and AG-UI leverage this to let you get structured outputs out of the agent and map that to some UI.

That state is shared between the UI and the backend. State can be messages — that's part of memory — but it doesn't have to be; it can be structured pieces of data as well. That's one of the really clean things about working memory: I can have structured data that my agent is aware of, can update and see, and my user can also update and see.

That state can be generated by the user, or by an agent — it's fully collaborative, it doesn't have to come from the agent. And it's bidirectional, as we'll see in a second: the user can make changes, the agent can make changes, and we can see all of it.

So if I ask it to enable app mode, it toggles that little slider in the top right, and starts adding some to-dos into our application — this is working memory behind the scenes. I can click through these and ask, "What are my to-dos now?" and the agent is aware of the updates I just made — it says they're all marked as completed. This is like a canvas application, where I can add a bunch of to-dos, mark one with a fire emoji and say "Finish talk," and ask it, "What do I need to do next?" It's aware of all those updates I just made, which is pretty cool.

Now we're on the tail end — let's talk about the code. We define a Zod object and bind it into our Mastra agent as working memory. In CopilotKit, we have a hook called useAgent, which gives us programmatic access through a unified interface to any agent. I then build a to-do-list application off of agent state.todos. The AG-UI protocol transmits state events from the Mastra agent as it executes, which I can then leverage and render inside my application. And I can have the user update that state through agent.setState — so the useAgent hook lets us update state programmatically as well as receive state from the agent reactively.

I want to talk a little bit about what's on the horizon as we finish out. As agents become more autonomous, we see that they're going to need more steering — more mid-run interruptions, more mid-run steering, to make sure the agent stays on task. If I spin up a Claude Code instance in the cloud and just let it go do its thing, I don't really have any jurisdiction over what it's doing outside of the initial prompt.

We find that steering is really important, which is great for some of the Mastra primitives like suspend and resume, which let it solicit feedback explicitly.

What's really interesting about this — we call it, and you've probably heard it, human-in-the-loop — is that this is actually great human signal. Who here has done annotated-data work, like at Scale AI or somewhere similar? Anyone? All right, who here has used Cursor before? Yeah — so all of you actually have annotated data. Cursor used all of your interactions with it to build their Composer model. Same thing with GPT, Codex, and so on.

This is really interesting, because as users interact with our agents, we're able to say, "this was the user gently steering you in one direction or another," which we can then train on top of. So one thing we're really excited about at CopilotKit is self-improving on top of reinforcement learning from human feedback.

It lets you collaborate with your user — just from the user naturally interacting with your application, they don't have to click a thumbs-up or thumbs-down button, or submit feedback explicitly. You naturally receive input from the user that you can then train on top of. That's something we're really trying to push on at CopilotKit right now, and we're really excited about it for the future.

If any of this interests you, by the way, we are hiring — go ahead and click through to CopilotKit.ai/careers if you don't want to scan it now. And that's been my talk. This is CopilotKit's repo, AG-UI's repo, and you can also book some time with us. Thank you.

Thank you so much. We have time for one question.

It's very interesting to see the different ways — especially the open-world approach to creating the user interface. But since you already mentioned it's relatively unpredictable and hard to control, what's the use case for that? It's cool that it can do it, but what's the practical use case?

Yeah, so if you've used Claude recently, Claude can now generate UI for you on the fly — if you ask it, "Hey, show me how electrons work," it can spin up a user interface to show you that. It's really great for showing the user something when you don't care what it looks like — it's more for the benefit of the user, for what the user wants. So if the user says, "Give me a table of all my data formatted like this, with colors like that," the agent can go try to do that — you never told the agent it could do that, it can just generate some HTML: "Here's your latest ten queries in a crazy bar chart I just invented." It's really great for disposable interactions where you don't care what it looks like — you just want to let the user get the information they want really quickly, and then you can throw it away right after. At CopilotKit, we also let you customize it quite heavily — there's a lot I can show with open generative UI that lets you insert UI "skills" and things like that, so the agent has more guidance on how you want your brand portrayed.

I know I said one question, but I saw so many hands fly up — I'd be remiss not to take one more, perhaps from this gentleman at the front. First off, thanks for doing a demo at demo day, so good on you. Second — you showed AG-UI, and of course the Google alternative. Obviously they're different — what do you recommend, and which one is the standard, in your opinion? Or the de facto one?

Oh yeah, yeah — so we own AG-UI, so we like to think we're the de facto standard. We're adopted quite widely — we work with Mastra pretty frequently, and we have about 3 million monthly downloads across all our AG-UI packages. We're adopted by quite a lot of people. AG-UI and A2UI actually don't compete at all — A2UI is a declarative schema for how UIs can or should look. So if an agent produces some structured output, that structured output could be A2UI, describing what an interface should look like, and then we map and bind that to some renderers so you can see it in the UI. Those flight cards, for example — those were renderers I matched, but the schema was from A2UI. AG-UI is transporting all of that data — AG-UI is kind of a superset of all of these. It lets us transport MCP app communication, it lets us transport A2A, and it lets us transport A2UI as well. The protocol is really built for streaming communication between a user and an agent. So I like to think both of these are going to be standards — I'd say AG-UI is already a standard, and A2UI is emerging. There are some pretty interesting releases coming out soon, so stay tuned on that. Hopefully that clarifies things.
