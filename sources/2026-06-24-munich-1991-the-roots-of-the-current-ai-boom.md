---
id: 2026-06-24-munich-1991-the-roots-of-the-current-ai-boom
title: "Munich 1991: the Roots of the Current AI Boom"
type: article
url: https://people.idsia.ch/~juergen/ai-boom-roots-munich-1991.html
captured: 2026-06-24
via: lobsters-ai
tags: [news, ai]
---

David Ha, Sakana AI

Jürgen Schmidhuber, KAUST & IDSIA

18 June 2026   @hardmaru

@SchmidhuberAI

AI Blog

## Munich 1991: the Roots of the Current AI Boom Preface by David Ha

When we look at the massive scale of today’s Artificial Intelligence boom, it is easy to forget that the foundations of this trillion-dollar industry were laid down over 30 years ago in Munich.

Today, the world's top tech companies are investing hundreds of billions into scaling up Large Language Models (LLMs) such as ChatGPT. Yet, outside of a few history buffs or old-school folks in the Machine Learning community, people might not realize that virtually every core building block of these modern systems was published in a span of just a few months back in 1991. Incredibly, they all emerged from a single lab at the Technical University Munich led by Jürgen Schmidhuber.

Before that year ended, his team had essentially mapped out the modern era of deep learning. They published the very first Transformer variant (see ChatGPT's "T"), introduced the concept of unsupervised pre-training (ChatGPT's "P"), and pioneered neural network distillation. They also introduced deep residual learning, the centerpiece of both LSTMs and ResNets, the most cited AI papers of the 20th and the 21st century, respectively. These four techniques power today's most advanced LLMs. Furthermore, they laid the early groundwork for generative adversarial networks, foundational for "Generative AI."

Jürgen’s contributions have deeply shaped my own thinking over the years, from my time at Google Brain to our recursive self-improvement (RSI) research we're currently pushing at Sakana AI. I am especially proud to have helped popularize World Models back in 2018, building directly on concepts his lab introduced in the 1990s.

It is amazing to see how well some of these ideas have stood the test of time, scaling up to be fully embraced by the global AI community! For those interested in the real history of deep learning, Jürgen has put together a detailed timeline below of exactly how these seeds were planted in Munich in 1991.

David Ha, June 2026

### Jürgen Schmidhuber's 1991 Timeline, with Annotated References

I am proud of the work my team did in 1991 in my home city when compute was millions of times more expensive than today [RAW], and of all the great people I worked with there and afterwards. Check out TU Munich's following key AI publications dated 3/26/1991—8/31/1991.

★ 26 March 1991: the first kind of Transformer (see the T in ChatGPT)—now called the unnormalized linear Transformer [ULTRA][FWP0-6][WHO10][DLH]: the predecessor of the normalized quadratic Transformer [TR1]. ULTRA is still important, also because of its efficiency: its computational costs scale *linearly* in input size, rather than *quadratically*.

★ 30 April 1991: Pre-Training for deep neural networks (NNs)—the P in ChatGPT [UN0][UN1][UN2][UN][DLH]. This enabled very deep learning [WHO5].

★ 30 April 1991: Neural network distillation—central to the famous 2025 DeepSeek "Sputnik" and other Large Language Models (LLMs) [UN0][UN1][UN2][WHO9][DLH].

★ 15 June 1991: deep residual learning with residual connections for very deep NNs [WHO11] (see Sepp Hochreiter's diploma thesis [VAN1]): the core ingredient of Long Short-Term Memory [LSTM1], the most cited AI of the 20th century, basis of the first LLMs in the 2010s (ELMO, ULMFiT).

The most-cited scientific article of the *21st* century [MOST25-26] is *also* about deep residual learning, focusing on a variant of our LSTM-inspired deep residual Highway Net [HW1-25b] that was 10 times deeper than previous feedforward NNs [WHO11][DLH]. Deep residual learning is now being used in virtually all LLMs.

★ 31 August 1991: first peer-reviewed publication [GAN91] on generative & adversarial networks [GAN90-25] for neural world models [WM26,WM26b] trained through artificial curiosity & creativity—now controversially used for deepfakes and other applications of Generative AI [WHO8][DLH].

As of January 2026, the two most frequently cited papers of all time (with the most citations within 3 years—manuals excluded) are directly based on the work of 1991 [MOST26][MOST][MIR]. In 1991, however, it was already totally obvious that LLM-like NNs alone are not enough to achieve *Artificial General Intelligence* (AGI). No AGI without mastery of the real world [DLH]! That's why we started working on additional techniques required to achieve AGI, e.g., planning with adaptive world models [PLAN1-6][WM26,WM26b] created by artificial scientists [AC] (since 1990 at TU Munich), meta learning & recursive self-improvement (since 1987) [META1][META], and others [DLH][AIB].

Around the same time, Munich also was the origin of the first self-driving cars in traffic [AUT] (by Ernst Dickmanns's team), going up to 175 km/h. The city was truly the epicenter of AI. In the past 3 decades, however, most of commercial AI has shifted to the Pacific Rim, far away from Munich. How could that happen? Can anything be done about it? See [95-25] for answers!

See [WHO3-11] for the broader historical context [DLH] of the work published in 1991 [MIR]. I am still hoping that I may live to see our great field of Machine Learning realize my 1970s teenager vision of building something much smarter than myself, such that I can retire.

Jürgen Schmidhuber, June 2026

## Acknowledgments

Thanks to several expert reviewers for useful comments. (Let us know if you can spot any remaining error.) The contents of this article may be used for educational and non-commercial purposes, including articles for Wikipedia and similar sites. This work is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.

## Annotated References

[95-25] J. Schmidhuber (AI Blog, 2025). 1995-2025: The Decline of Germany & Japan vs US & China. Can All-Purpose Robots Fuel a Comeback? In 1995, in terms of nominal gross domestic product (GDP), a combined Germany and Japan were almost 1:1 economically with a combined USA and China, according to IMF. Only 3 decades later, this ratio is now down to 1:5! Self-replicating AI-driven all-purpose robots may be the answer. Based on a 2024 F.A.Z. guest article.

[AC] J. Schmidhuber (AI Blog, 2021, updated 2025).  3 decades of artificial curiosity & creativity. * Schmidhuber's artificial scientists not only answer given questions but also invent new questions. They achieve curiosity through: (1990) the principle of generative adversarial networks, (1991) neural nets that maximise learning progress, (1995) neural nets that maximise information gain (optimally since 2011), (1997) adversarial design of surprising computational experiments, (2006) maximizing compression progress like scientists/artists/comedians do, (2011) PowerPlay... Since 2012: applications to real robots.*

[AIB] J. Schmidhuber's AI Blog. With lessons on the history of AI & computing, e.g.: Who invented deep learning? Who invented backpropagation? Who invented convolutional neural networks? Who invented artificial neural networks? Who invented generative adversarial networks? Who invented Transformer neural networks? Who invented deep residual learning? Who invented neural knowledge distillation? Who invented the computer? Who invented the transistor? Who invented the integrated circuit? ...

[ATT] J. Schmidhuber (AI Blog, 2020, updated 2025). 30-year anniversary of end-to-end differentiable sequential neural attention. Plus goal-conditional reinforcement learning. *Schmidhuber had both hard attention for foveas (1990) and soft attention in form of Transformers with linearized self-attention (1991-93).[FWP] Today, both types are very popular.*

[AUT] J. Schmidhuber (AI Blog, 2005). Highlights of robot car history. *Around 1986, Ernst Dickmanns and his group at Univ. Bundeswehr Munich built the world's first real autonomous robot cars, using saccadic vision, probabilistic approaches such as Kalman filters, and parallel computers. By 1994, they were in highway traffic, at up to 180 km/h, automatically passing other cars.*

[DLH] J. Schmidhuber. Annotated History of Modern AI and Deep Learning. Technical Report IDSIA-22-22, IDSIA, Switzerland, 2022, updated 2025. Preprint arXiv:2212.11279. Tweet.

[DLP] J. Schmidhuber.  How 3 Turing awardees republished key methods and ideas whose creators they failed to credit. Technical Report IDSIA-23-23, Swiss AI Lab IDSIA, 14 Dec 2023, updated 2025. Tweet of 2023.

[DS1] DeepSeek-AI (2025). DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning. Preprint arXiv:2501.12948. See the popular DeepSeek tweet of Jan 2025.

[FWP] J. Schmidhuber (AI Blog, 26 March 2021, updated 2025). 26 March 1991: Neural nets learn to program neural nets with fast weights—like Transformer variants. 2021: New stuff!  See tweet of 2022.*

[FWP0] J. Schmidhuber. Learning to control fast-weight memories: An alternative to recurrent nets. Technical Report FKI-147-91, Institut für Informatik, Technische Universität München, 26 March 1991. PDF. *First paper on neural fast weight programmers that separate storage and control: a slow net learns by gradient descent to compute weight changes of a fast net. The outer product-based version (Eq. 5) is now known as the unnormalized linear Transformer or the "Transformer with linearized self-attention."[ULTRA][FWP]*

[FWP1] J. Schmidhuber. Learning to control fast-weight memories: An alternative to recurrent nets. Neural Computation, 4(1):131-139, 1992. Based on [FWP0]. PDF. HTML.  Pictures (German). See tweet of 2022 for 30-year anniversary.

[FWP2] J. Schmidhuber. Reducing the ratio between learning complexity and number of time-varying variables in fully recurrent nets. In Proceedings of the International Conference on Artificial Neural Networks, Amsterdam, pages 460-463. Springer, 1993. PDF. *A recurrent extension of the unnormalized linear Transformer,[ULTRA] introducing the terminology of learning "internal spotlights of attention." First recurrent NN-based fast weight programmer using outer products to program weight matrices.*

[FWP3a] I. Schlag, J. Schmidhuber. Learning to Reason with Third Order Tensor Products. Advances in Neural Information Processing Systems (N(eur)IPS), Montreal, 2018. Preprint: arXiv:1811.12143. PDF.

[FWP6] I. Schlag, K. Irie, J. Schmidhuber. Linear Transformers Are Secretly Fast Weight Programmers. ICML 2021. Preprint: arXiv:2102.11174.

[GAN90] J. Schmidhuber. Making the world differentiable: On using fully recurrent self-supervised neural networks for dynamic reinforcement learning and planning in non-stationary environments. Technical Report FKI-126-90, TUM, Feb 1990, revised Nov 1990. PDF. *The first paper on planning with reinforcement learning recurrent neural networks (NNs) and recurrent world models (more), and on generative adversarial networks where a generator NN is fighting a predictor NN in a minimax game (more). Apparently, it was also the first paper of this kind to use the term "world model" for the predictor NN (although the basic concept of a world model is much older than that.) *

[GAN91] J. Schmidhuber. A possibility for implementing curiosity and boredom in model-building neural controllers. In J. A. Meyer and S. W. Wilson, editors, *Proc. of the International Conference on Simulation of Adaptive Behavior: From Animals to Animats*, pages 222-227. MIT Press/Bradford Books, 1991. PDF. More. Based on [GAN90].

[GAN10] J. Schmidhuber. Formal Theory of Creativity, Fun, and Intrinsic Motivation (1990-2010). * IEEE Transactions on Autonomous Mental Development*, 2(3):230-247, 2010. IEEE link. PDF. This well-known 2010 survey summarised the generative adversarial NNs of 1990 as follows: a *"neural network as a predictive world model is used to maximize the controller's intrinsic reward, which is proportional to the model's prediction errors"* (which are minimized).

[GAN10b] O. Niemitalo. A method for training artificial neural networks to generate missing data within a variable context. Blog post, Internet Archive, 2010. *A blog post describing the basic ideas[GAN90-91][GAN20][AC] of GANs.*

[GAN14] I. Goodfellow, J. Pouget-Abadie, M. Mirza, B. Xu, D. Warde-Farley, S. Ozair, A. Courville, Y. Bengio. Generative adversarial nets. NIPS 2014, 2672-2680, Dec 2014. *A description of GANs that does not cite Schmidhuber's original GAN principle of 1990[GAN90-91][GAN20][AC][R2][DLP] and contains wrong claims about Schmidhuber's adversarial NNs for Predictability Minimization.[PM0-2][GAN20][DLP]*

[GAN19] T. Karras, S. Laine, T. Aila. A style-based generator architecture for generative adversarial networks. In Proc. IEEE Conf. on Computer Vision and Pattern Recognition (CVPR), pages 4401-4410, 2019.

[GAN19b] D. Fallis. The epistemic threat of deepfakes. Philosophy & Technology 34.4 (2021):623-643.

[GAN20] J. Schmidhuber. Generative Adversarial Networks are Special Cases of Artificial Curiosity (1990) and also Closely Related to Predictability Minimization (1991). Neural Networks, Volume 127, p 58-66, 2020. Preprint arXiv/1906.04493.

[GAN25] J. Schmidhuber. Who Invented Generative Adversarial Networks? Technical Note IDSIA-14-25, IDSIA, December 2025.

[HW] J. Schmidhuber (AI Blog, 2015, updated 2025 for 10-year anniversary). Overview of Highway Networks: First working really deep feedforward neural networks with hundreds of layers.

[HW1] R. K. Srivastava, K. Greff, J. Schmidhuber. Highway networks. Preprints arXiv:1505.00387 (May 2015) and arXiv:1507.06228 (Training Very Deep Networks; July 2015). Also at NeurIPS 2015. *The first working very deep gradient-based feedforward neural nets (FNNs) with hundreds of layers, ten times deeper than previous gradient-based FNNs. Let g, t, h, denote non-linear differentiable functions. Each non-input layer of a Highway Net computes g(x)x + t(x)h(x), where x is the data from the previous layer. The gates g(x) are typically initialised to 1.0, to obtain *plain* residual connections (weight 1.0) [VAN1][HW25]. This allows for very deep error propagation, which makes Highway NNs so deep. The later Resnet (Dec 2015) [HW2] adopted this principle. It is like a Highway net variant whose gates are always open: g(x)=t(x)=const=1. That is, Highway Nets are gated ResNets: set the gates to 1.0→ResNet. The residual parts of a Highway Net are like those of an unfolded 1999 LSTM [LSTM2a], while the residual parts of a ResNet are like those of an unfolded 1997 LSTM [LSTM1][HW25]. Highway Nets perform roughly as well as ResNets on ImageNet [HW3]. Variants of Highway gates are also used for certain algorithmic tasks, where plain residual layers do not work as well [NDR]. See also [HW25]: who invented deep residual learning? More.*

[HW1a] R. K. Srivastava, K. Greff, J. Schmidhuber. Highway networks. Presentation at the Deep Learning Workshop, ICML'15, July 10-11, 2015. Link.

[HW2] He, K., Zhang, X., Ren, S., Sun, J. Deep residual learning for image recognition. Preprint arXiv:1512.03385 (Dec 2015). *Microsoft's ResNet paper refers to the Highway Net (May 2015) [HW1] as 'concurrent'. However, this is incorrect: ResNet was published seven months later. Although the ResNet paper acknowledges the problem of vanishing/exploding gradients, it fails to recognise that S. Hochreiter first identified the issue in 1991 and developed the residual connection solution (weight 1.0) [VAN1][HW25]. The ResNet paper cites the earlier Highway Net in a way that does not make it clear that ResNets are essentially open-gated Highway Nets and that Highway Nets are gated ResNets. It also fails to mention that the gates of residual connections in Highway Nets are initially open (1.0), meaning that Highway Nets start out with standard residual connections, to achieve deep residual learning (Highway Nets were ten times deeper than previous gradient-based feedforward nets). The residual parts of a Highway Net are like those of an unfolded 1999 LSTM [LSTM2a], while the residual parts of a ResNet are like those of an unfolded 1997 LSTM [LSTM1][HW25]. A follow-up paper by the ResNet authors was flawed in its design, leading to incorrect conclusions about gated residual connections [HW25b]. See also [HW25]: who invented deep residual learning? More.*

[HW3] K. Greff, R. K. Srivastava, J. Schmidhuber. Highway and Residual Networks learn Unrolled Iterative Estimation. Preprint arxiv:1612.07771 (2016). Also at ICLR 2017.

[HW25] J. Schmidhuber. Who Invented Deep Residual Learning? Technical Report IDSIA-09-25, IDSIA, 2025. Preprint arXiv:2509.24732. 

[HW25b] R. K. Srivastava (January 2025). Weighted Skip Connections are Not Harmful for Deep Nets. *Shows that a follow-up paper by the authors of [HW2] suffered from design flaws leading to incorrect conclusions about gated residual connections.*

[LIL4] J. Schmidhuber. 2025: centennial of the transistor, patented by Julius Edgar Lilienfeld in 1925-1928. Technical Note IDSIA-10-25, IDSIA, 22 Oct 2025.

[LSTM0] S. Hochreiter and J. Schmidhuber.  Long Short-Term Memory.  TR FKI-207-95, TUM, August 1995. PDF.

[LSTM1a] S. Hochreiter and J. Schmidhuber. LSTM can solve hard long time lag problems. Proceedings of the 9th International Conference on Neural Information Processing Systems (NIPS'96). Cambridge, MA, USA, MIT Press, p. 473–479.

[LSTM1] S. Hochreiter, J. Schmidhuber. Long Short-Term Memory. Neural Computation, 9(8):1735-1780, 1997. PDF. Based on [LSTM0]. More.

[LSTM2] F. A. Gers, J. Schmidhuber, F. Cummins. Learning to Forget: Continual Prediction with LSTM. Neural Computation, 12(10):2451-2471, 2000. PDF. *The "vanilla LSTM architecture" with forget gates that everybody is using today, e.g., in Google's Tensorflow.*

[LSTM2] F. A. Gers, J. Schmidhuber, F. Cummins. Learning to Forget: Continual Prediction with LSTM. In Proc. Int. Conf. on Artificial Neural Networks (ICANN'99), Edinburgh, Scotland, p. 850-855, IEE, London, 1999. *The "vanilla LSTM architecture" with forget gates that everybody is using today, e.g., in Google's Tensorflow.*

[LSTM3] A. Graves, J. Schmidhuber. Framewise phoneme classification with bidirectional LSTM and other neural network architectures. Neural Networks, 18:5-6, pp. 602-610, 2005. PDF.

[LSTM4] S. Fernandez, A. Graves, J. Schmidhuber. An application of recurrent neural networks to discriminative keyword spotting. *Intl. Conf. on Artificial Neural Networks ICANN'07,* 2007. PDF.

[LSTM5] A. Graves, M. Liwicki, S. Fernandez, R. Bertolami, H. Bunke, J. Schmidhuber. A Novel Connectionist System for Improved Unconstrained Handwriting Recognition. IEEE Transactions on Pattern Analysis and Machine Intelligence, vol. 31, no. 5, 2009. PDF.

[LSTM6] A. Graves, J. Schmidhuber. Offline Handwriting Recognition with Multidimensional Recurrent Neural Networks. NIPS'22, p 545-552, Vancouver, MIT Press, 2009. PDF.

[LSTM7] J. Bayer, D. Wierstra, J. Togelius, J. Schmidhuber. Evolving memory cell structures for sequence learning. Proc. ICANN-09, Cyprus, 2009. PDF.

[META] J. Schmidhuber (AI Blog, 2020). 1/3 century anniversary of first publication on metalearning machines that learn to learn (1987). *For its cover I drew a robot that bootstraps itself. 1992-: gradient descent-based neural metalearning. 1994-: Meta-Reinforcement Learning with self-modifying policies. 1997: Meta-RL plus artificial curiosity and intrinsic motivation. 2002-: asymptotically optimal metalearning for curriculum learning. 2003-: mathematically optimal Gödel Machine. 2020: new stuff!*

[META1] J. Schmidhuber. Evolutionary principles in self-referential learning, or on learning how to learn: The meta-meta-... hook. Diploma thesis, Institut für Informatik, Technische Universität München, 1987. Searchable PDF scan (created by OCRmypdf which uses LSTM). HTML. *For example,  Genetic Programming  (GP) is applied to itself, to recursively evolve better GP methods through Meta-Evolution. More.*

[MIR] J. Schmidhuber (Oct 2019, updated '21, '22, '25, '26). Deep Learning: Our Miraculous Year 1990-1991. Preprint arXiv:2005.05744. *The Deep Learning Artificial Neural Networks (NNs) of our team have revolutionised Machine Learning & AI. Many of the basic ideas behind this revolution were published within the 12 months of our *"Annus Mirabilis"* 1990-1991 at our lab in TU Munich. Back then, few people were interested. But a quarter century later, NNs based on our *"Miraculous Year"* were on over 3 billion devices, and used many billions of times per day, consuming a significant fraction of the world's compute. In particular, in 1990-91, we laid foundations of Generative AI, publishing principles of (1) Generative Adversarial Networks for Artificial Curiosity and Creativity (now used for deepfakes), (2) Transformers (the T in ChatGPT—see the 1991 Unnormalized Linear Transformer), (3) Pre-training for deep NNs (see the P in ChatGPT), (4) NN distillation (key for DeepSeek), and (5) recurrent World Models for Reinforcement Learning and Planning in partially observable environments. The year 1991 also marks the emergence of the defining features of (6) LSTM, the most cited AI paper of the 20th century (based on deep residual learning through residual NN connections), and (7) the most cited paper of the 21st century, based on our LSTM-inspired Highway Net that was 10 times deeper than previous feedforward NNs. As of 2025, the two most frequently cited scientific articles of all time (with the most Google Scholar citations within 3 years—manuals excluded) are both directly based on our 1991 work. *

[MOST] J. Schmidhuber (AI Blog, 2021, updated 2025). The most cited neural networks all build on work done in my labs: * 1. Long Short-Term Memory (LSTM), the most cited AI of the 20th century. 2. ResNet (open-gated Highway Net), the most cited AI of the 21st century. 3. AlexNet & VGG Net (the similar but earlier DanNet of 2011 won 4 image recognition challenges before them). 4. GAN (an instance of Adversarial Artificial Curiosity of 1990). 5. Transformer variants—see the 1991 unnormalised linear Transformer (ULTRA). Foundations of Generative AI were published in 1991: the principles of GANs (now used for deepfakes), Transformers (the T in ChatGPT), Pre-training for deep NNs (the P in ChatGPT), NN distillation, and the famous DeepSeek—see the tweet.* As of 2025, the two most frequently cited scientific articles of all time (with the most Google Scholar citations within 3 years—manuals excluded) are both directly based on our 1991 work.

[MOST25] H. Pearson, H. Ledford, M. Hutson, R. Van Noorden. Exclusive: the most-cited papers of the twenty-first century. Nature, 15 April 2025.

[MOST25b] R. Van Noorden. Science’s golden oldies: the decades-old research papers still heavily cited today. Nature, 15 April 2025.

[MOST26] J. Schmidhuber. The two most frequently cited papers of all time are based on our 1991 work. Technical Note IDSIA-1-26, January 2026.

[PLAN] J. Schmidhuber (AI Blog, 2020). 30-year anniversary of planning & reinforcement learning with recurrent world models and artificial curiosity (1990). *This work also introduced high-dimensional reward signals, deterministic policy gradients for RNNs, and the GAN principle (widely used today). Agents with adaptive recurrent world models even suggest a simple explanation of consciousness & self-awareness.*

[PLAN1] J. Schmidhuber. Making the world differentiable: On using fully recurrent self-supervised neural networks for dynamic reinforcement learning and planning in non-stationary environments. Technical Report FKI-126-90, TUM, Feb 1990, revised Nov 1990. PDF. *The first paper on long-term planning with self-supervised reinforcement learning recurrent neural networks (NNs) and recurrent predictive world models (more), and on generative adversarial networks where a generator NN is fighting a predictor NN in a minimax game (more). Apparently, it was also the first paper of this kind to use the term "world model" for the predictor NN (although the basic concept of a world model is much older than that.) *

[PLAN2] J. Schmidhuber.  An on-line algorithm for dynamic reinforcement learning and planning in reactive environments.  *Proc. IEEE/INNS International Joint Conference on Neural Networks, San Diego*, volume 2, pages 253-258, June 17-21, 1990. Based on TR FKI-126-90 (1990) [PLAN1]. More.

[PLAN3] J. Schmidhuber. Reinforcement learning in Markovian and non-Markovian environments. In D. S. Lippman, J. E. Moody, and D. S. Touretzky, editors, * Advances in Neural Information Processing Systems 3, NIPS'3*, pages 500-506. San Mateo, CA: Morgan Kaufmann, 1991. PDF. Partially based on [PLAN1].

[PLAN4] J. Schmidhuber. On Learning to Think: Algorithmic Information Theory for Novel Combinations of Reinforcement Learning Controllers and Recurrent Neural World Models. Report arXiv:1210.0118 [cs.AI], 2015. *This paper went beyond the inefficient *millisecond by millisecond planning* of 1990 [PLAN1], addressing planning and reasoning in *abstract concept spaces*. The controller C became an *RL prompt engineer* that learns to create a *chain of thought*: to speed up RL, C learns to query its world model for abstract reasoning and decision making.*

[PLAN5] One Big Net For Everything. Preprint arXiv:1802.08864 [cs.AI], Feb 2018. *This paper collapsed the control network and the world model network of [PLAN4] into a single *One Big Net* for everything, using my neural distillation procedure of 1991 [UN0-1]. Apparently, this is what DeepSeek used to shock the stock market in 2025.*

[PLAN6] D. Ha, J. Schmidhuber. Recurrent World Models Facilitate Policy Evolution. Advances in Neural Information Processing Systems (NIPS), Montreal, 2018. (Talk.) Preprint: arXiv:1809.01999. Github: World Models.

[PM0] J. Schmidhuber. Learning factorial codes by predictability minimization. TR CU-CS-565-91, Univ. Colorado at Boulder, 1991. PDF. More.

[PM1] J. Schmidhuber. Learning factorial codes by predictability minimization. Neural Computation, 4(6):863-879, 1992. Based on [PM0], 1991. PDF. More.

[PM2] J. Schmidhuber, M. Eldracher, B. Foltin. Semilinear predictability minimzation produces well-known feature detectors. Neural Computation, 8(4):773-786, 1996. PDF. More.

[R2] Reddit/ML, 2019. J. Schmidhuber really had GANs in 1990.

[RAW] J. Schmidhuber (AI Blog, 2001). Raw Computing Power.

[TR1] A. Vaswani, N. Shazeer, N. Parmar, J. Uszkoreit, L. Jones, A. N. Gomez, L. Kaiser, I. Polosukhin (2017). Attention is all you need. NIPS 2017, pp. 5998-6008. * This paper introduced the name "Transformers" for a now widely used NN type. It did not cite the 1991 publication on what's now called unnormalized "linear Transformers" with "linearized self-attention."[ULTRA] Schmidhuber also introduced the now popular attention terminology in 1993.[ATT][FWP2][R4] See tweet of 2022 for 30-year anniversary. *

[TR2] J. Devlin, M. W. Chang, K. Lee, K. Toutanova (2018). Bert: Pre-training of deep bidirectional Transformers for language understanding. Preprint arXiv:1810.04805.

[TR3] K. Tran, A. Bisazza, C. Monz. The Importance of Being Recurrent for Modeling Hierarchical Structure. EMNLP 2018, p 4731-4736. ArXiv preprint 1803.03585.

[TR4] M. Hahn. Theoretical Limitations of Self-Attention in Neural Sequence Models. Transactions of the Association for Computational Linguistics, Volume 8, p.156-171, 2020.

[TR5] A. Katharopoulos, A. Vyas, N. Pappas, F. Fleuret. Transformers are RNNs: Fast autoregressive Transformers with linear attention. In Proc. Int. Conf. on Machine Learning (ICML), July 2020.

[TR5a] Z. Shen, M. Zhang, H. Zhao, S. Yi, H. Li. Efficient Attention: Attention with Linear Complexities. WACV 2021.

[TR6] K. Choromanski, V. Likhosherstov, D. Dohan, X. Song, A. Gane, T. Sarlos, P. Hawkins, J. Davis, A. Mohiuddin, L. Kaiser, et al. Rethinking attention with Performers. In Int. Conf. on Learning Representations (ICLR), 2021.

[TR6a] H. Peng, N. Pappas, D. Yogatama, R. Schwartz, N. A. Smith, L. Kong. Random Feature Attention. ICLR 2021.

[TR7] S. Bhattamishra, K. Ahuja, N. Goyal. On the Ability and Limitations of Transformers to Recognize Formal Languages. EMNLP 2020.

[TR8] W. Merrill, A. Sabharwal. The Parallelism Tradeoff: Limitations of Log-Precision Transformers. TACL 2023.

[TR25] J. Schmidhuber. Who Invented Transformer Neural Networks? Technical Note IDSIA-11-25, IDSIA, Switzerland, Nov 2025.

[ULTRA] References on the 1991 unnormalized linear Transformer (ULTRA): original tech report (March 1991) [FWP0]. Journal publication (1992) [FWP1]. Recurrent ULTRA extension (1993) introducing the terminology of learning "internal spotlights of attention” [FWP2]. Modern *"quadratic"* Transformer (2017: *"attention is all you need"*) scaling *quadratically* in input size [TR1]. 2020 paper [TR5] using the terminology *"linear Transformer"* for a more efficient Transformer variant that scales *linearly*, leveraging *linearized attention* [TR5a]. 2021 paper [FWP6] pointing out that ULTRA dates back to 1991 [FWP0] when compute was a million times more expensive. Overview of ULTRA and other Fast Weight Programmers (2021) [FWP]. See the T in ChatGPT! See also surveys [DLH][DLP], 2022 tweet for ULTRA's 30-year anniversary, and 2024 tweet.

[UN] J. Schmidhuber (AI Blog, 2021, updated 2025). 1991: First very deep learning with unsupervised pre-training (see the P in ChatGPT). First neural network distillation (key for DeepSeek). *Unsupervised hierarchical predictive coding (with self-supervised target generation) finds compact internal representations of sequential data to facilitate downstream deep learning. The hierarchy can be distilled into a single deep neural network (suggesting a simple model of conscious and subconscious information processing). 1993: solving problems of depth >1000.*

[UN0] J. Schmidhuber. Neural sequence chunkers. Technical Report FKI-148-91, Institut für Informatik, Technische Universität München, April 1991. PDF. * Unsupervised/self-supervised pre-training for deep neural networks (see the P in ChatGPT) and predictive coding is used in a deep hierarchy of recurrent nets (RNNs) to find compact internal representations of long sequences of data, across multiple time scales and levels of abstraction. Each RNN tries to solve the *pretext task* of predicting its next input, sending only unexpected inputs to the next RNN above. The resulting compressed sequence representations greatly facilitate downstream supervised deep learning such as sequence classification. By 1993, the approach solved problems of depth 1000 [UN2] (requiring 1000 subsequent computational stages/layers—the more such stages, the deeper the learning). A variant collapses the hierarchy into a single deep net. It uses a so-called *conscious chunker RNN* which attends to unexpected events that surprise a lower-level so-called *subconscious automatiser RNN.* The chunker learns to *understand* the surprising events by predicting them. The automatiser uses a neural knowledge distillation procedure (key for the famous 2025 DeepSeek) to compress and absorb the formerly *conscious* insights and behaviours of the chunker, thus making them *subconscious.* The systems of 1991 allowed for much deeper learning than previous methods.*

[UN1] J. Schmidhuber. Learning complex, extended sequences using the principle of history compression. Neural Computation, 4(2):234-242, 1992. Based on TR FKI-148-91, TUM, 1991.[UN0] PDF. *First working Deep Learner based on a deep RNN hierarchy (with different self-organising time scales), overcoming the vanishing gradient problem through unsupervised pre-training of deep NNs (see the P in ChatGPT) and predictive coding (with self-supervised target generation). Also: compressing or distilling a teacher net (the chunker) into a student net (the automatizer) that does not forget its old skills—such approaches are now widely used, e.g., by DeepSeek. See also this tweet. More.*

[UN2] J. Schmidhuber. Habilitation thesis, TUM, 1993. PDF. *An ancient experiment on "Very Deep Learning" with credit assignment across 1200 time steps or virtual layers and unsupervised / self-supervised pre-training for a stack of recurrent NN can be found here (depth > 1000). See also Sec. 5.5 on *"Vorhersagbarkeitsmaximierung"* (Predictability Maximization).*

[VAN1] S. Hochreiter. Untersuchungen zu dynamischen neuronalen Netzen. Diploma thesis, TUM, 1991 (advisor J. Schmidhuber). PDF. More on the Fundamental Deep Learning Problem.

[WHO3] J. Schmidhuber (AI Blog, 2025). Who invented the transistor? Based on [LIL4].

[WHO4] J. Schmidhuber. Who invented artificial neural networks? Technical Note IDSIA-15-25, IDSIA, Switzerland, Nov 2025.

[WHO5] J. Schmidhuber. Who invented deep learning? Technical Note IDSIA-16-25, IDSIA, Switzerland, Nov 2025.

[WHO6] J. Schmidhuber (AI Blog, 2014; updated 2025). Who invented backpropagation? See also LinkedIn post.

[WHO7] J. Schmidhuber. Who invented convolutional neural networks? Technical Note IDSIA-17-25, IDSIA, Switzerland, 2025. See popular tweet.

[WHO8] J. Schmidhuber. Who Invented Generative Adversarial Networks? Technical Note IDSIA-14-25, IDSIA, Switzerland, Dec 2025.

[WHO9] J. Schmidhuber. Who invented knowledge distillation with artificial neural networks? Technical Note IDSIA-12-25, IDSIA, Nov 2025.

[WHO10] J. Schmidhuber. Who Invented Transformer Neural Networks? Technical Note IDSIA-11-25, IDSIA, Switzerland, Nov 2025.

[WHO11] J. Schmidhuber. Who Invented Deep Residual Learning? Technical Report IDSIA-09-25, IDSIA, Switzerland, Sept 2025. Preprint arXiv:2509.24732.

[WHO12] J. Schmidhuber. Who invented JEPA? Technical Note IDSIA-3-22, IDSIA, Switzerland, March 2026.

[WM26] J. Schmidhuber. The Neural World Model Boom. Technical Note IDSIA-2-26, 4 Feb 2026 (updated April 2024).

[WM26b] J. Schmidhuber. Simple but powerful ways of using world models and their latent space. Opening Keynote at the World Modeling Workshop, Agora, Mila - Quebec AI Institute, 4 Feb 2026. Also on YouTube (starts around 10:44). See video tweet.
