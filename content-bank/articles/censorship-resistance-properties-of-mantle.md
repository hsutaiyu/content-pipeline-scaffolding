---
title: "Censorship Resistance Properties of Mantle"
source: https://medium.com/0xmantle/censorship-resistance-properties-of-mantle-e34e31101fc8
published: 2023-03-03
note: Writing sample for voice reference.
---

# **Censorship Resistance Properties of Mantle**

[![Mantle Network](https://miro.medium.com/v2/resize:fill:32:32/0*w-6d4VpYha0olTgb.jpg)](https://medium.com/@mantlenetwork.eth?source=post_page---byline--e34e31101fc8-----------------------------------------)

[Mantle Network](https://medium.com/@mantlenetwork.eth?source=post_page---byline--e34e31101fc8-----------------------------------------)

Mar 3, 2023

428

1

## Combating Censorship on Layer 2

Blockchain networks and cryptocurrencies use public ledgers to store data that remains accessible to anyone at all times, and can be verified for its correctness. Because blockchains are immutable by nature, it means they are resistant to a single entity that attempts to modify or reverse any type of transactions or information that has been recorded on-chain. So blockchains, to a certain extent, are censorship-resistant by the virtue of being immutable.

While this may be the case for any data that makes its way to the chain, there is another aspect that is worth thinking about: And that is what sort of data is _allowed_ to be recorded on-chain. What are the threats to the openness and credible neutrality of public chains like Ethereum on the global stage? What sort of consequences does censorship ensue? Let’s explore the intriguing world of transaction censorship on public blockchain networks, and develop a better understanding of how modular layer-2 (L2) rollup networks like Mantle come into the picture with potential solutions. We’ll be going over:

1. Impact of regulation on public blockchain networks
2. Block production complications that arise due to factors such as Maximum Extractable Value (MEV)
3. The current state of optimistic rollup protocols
4. Mantle and its properties as a potential solution

## Controversy Around Regulation and Sanctions

The founder and CEO of now-bankrupt cryptocurrency exchange FTX, Sam Bankman-Fried, more popularly known as SBF, published an article last year proposing blocklists, a method to block on-chain interaction for specific wallet addresses that exhibit suspicious behavior, or have been a part of nefarious activities, essentially blacklisting them. ( [Original article](https://www.ftxpolicy.com/posts/possible-digital-asset-industry-standards))

This is in compliance with the [guidelines](https://home.treasury.gov/policy-issues/financial-sanctions/specially-designated-nationals-and-blocked-persons-list-sdn-human-readable-lists) published by the U.S. Office of Foreign Assets Control (OFAC) by maintaining “an on-chain list of the sanctioned addresses, updated in real time, maintained either by OFAC or by a responsible actor”.

Needless to say this attracted a lot of flak from the crypto community. Blockchains are designed to be permissionless and decentralized. Moving away from this basic principle defeats the entire purpose of cryptocurrencies. This form of censorship can be implemented by a regulatory-compliant block producer that can prohibit transactions from banned addresses, like we’re already seeing a big portion of Ethereum blocks being produced as per OFAC guidelines after the [Tornado sanctioning](https://home.treasury.gov/news/press-releases/jy0916).

_Source:_ [_https://www.mevwatch.info_](https://www.mevwatch.info/)

Nevertheless, even though censored transactions might get finalized more slowly, the non-censoring nodes in the network still eventually pick up and record them.

## Implications of MEV

The block rewards are the primary incentive for validators to keep the chain up and running. Validators can earn higher rewards for block generation by selecting the transactions sent with the highest amount of gas fees from the queue and optimizing the order in which they are included in a block. This involves re-ordering of pending transactions and executing them in an order that is different from the order in which they were originally sent to the network. The maximum amount of value that can be generated through this process is referred to as Maximum Extractable Value, or MEV. Today many well-known exchanges and staking pools implement and use censoring MEV relays. The problem is amplified by the fact that they also have some of the largest validator networks.

_Source:_ [_https://www.mevwatch.info_](https://www.mevwatch.info/)

_Source:_ [_https://beaconcha.in/pools#distribution_](https://beaconcha.in/pools#distribution)

MEV opens up the possibility of harmful behavior such as front-running and sandwich attacks. The end goal of such practices is to make sure all trades are always completed at the highest possible gas prices, which results in a sub-optimal user experience. To overcome this problem, many non-censoring validators also use MEV-boost relays, essentially a network of block producers that use sophisticated techniques to make sure they produce the best blocks while maintaining transaction sequence. But validators need to pay a fee to avail this service.

## Get Mantle Network’s stories in your inbox

How does any of this affect the way rollups operate? Read on to find out.

## Current State of Optimistic Rollups

The main goal of L2 solutions is to scale Ethereum’s performance while maintaining the same degree of security. Rollup solutions are very promising in terms of feasibility and practicality based on the current state of cryptographic technology.

Optimistic rollup protocols generally have a network component referred to as a sequencer. It receives and records transactions from users, groups them together into batches, and then runs them on a separate execution layer, or off-chain. However, most rollup protocols use a single sequencer that takes care of transaction ordering and block generation.

This is a potential weakness, since a sequencer is put in a privileged position to maintain complete control over transaction batch submission and ordering. The centralized sequencer has the ability to extract MEV by front-running user transactions. What’s even more concerning is that centralized sequencers may also be required to censor transactions by local laws and sanctions that are effective in the particular region.

## Mantle’s Approach to Censorship Resistance

[Mantle](http://mantle.xyz/) is a modular technology stack to scale Ethereum, built with high performance and low fees in mind without compromising on security. We’re working on a bunch of exciting features such as Multi-Party Computation (MPC), a decentralized sequencer, improved fraud proof mechanism, modular data availability, and more, in pursuit of decentralization, ease of use, and of course censorship resistance. Let’s go over the ones that are built to enhance censorship resistance on Mantle.

### Decentralizing the Rollup Sequencer

Centralized sequencers have exclusive write access to contracts on the data availability/base layer to which they submit transaction batches. We plan on implementing a sequencer network instead of a singular sequencer in an effort to distribute this write access privilege across a permissionless network, and simultaneously eliminate the single point of failure, which also helps avoid censorship related policies from particular jurisdictions.

On Mantle, we implement a scheduler as a part of the sequencer network with multiple goals in mind, one of them being reducing MEV by taking away the ability of sequencers to decide which transactions to include in a block, and another being censorship resistance. To read up on more details on the different kinds of roles within the sequencer network and its architecture, feel free to check out [our docs](https://docs.mantle.xyz/network-architecture/decentralized-sequencer-architecture).

Simply put, if the sequencer that is elected to produce the block for a particular epoch fails to do so for any reason at all, the scheduler will slash their bond and simply choose another sequencer. This disincentivizes censorship and any other kind of malicious behavior on part of block producers.

### Modular Data Availability

The data availability layer consists of a set of nodes that store transaction data that remains available for network actors to retrieve and reconstruct the current L2 state.

We plan on [implementing EigenLayer’s data availability solution](https://docs.mantle.xyz/introducing-mantle/a-gentle-introduction/solving-data-availability), better known as **EigenDA.** It will allow any willing Ethereum nodes to provide data availability services to the Mantle network and participate in Mantle’s economic model via $BIT staking. This will help ensure block data completeness and correctness on the Mantle execution layer, while simultaneously taking advantage of L1 security features.

A modular data availability model promotes censorship resistance by ensuring that the most updated block data is accessible to all network actors, including prospective block producers who can reconstruct the chain’s state at any point and start producing new blocks. There are no L2 actors who can influence this process in any manner by arbitrarily pausing block production and censoring or blocking users. The availability of state data in this fashion also means that invalid state transitions and censorship can be challenged by any network actors.

## Conclusion

Censorship resistance is an important fundamental objective of blockchain-based systems and cryptocurrencies, right up there with decentralization. New solutions and technology such as modular data availability and sharding are going to take Ethereum’s performance to the next level. They’re even more crucial because scaling cannot come at the expense of security or functionality.

We’re building the next generation of modular rollup solutions on [Mantle](http://mantle.xyz/) and a rich ecosystem of fun dApps around them with exactly that in mind. Feel free to browse through our [tech docs](http://docs.mantle.xyz/) and [GitHub](https://github.com/mantlenetworkio/mantle#readme) to find out what we’re working on. If your vision aligns with ours, you can get in touch with us through our [Discord server](https://discord.com/invite/0xMantle), or via this [onboarding form](https://airtable.com/shr9ATBlHZXCKDbPV).

[Censorship Resistance](https://medium.com/tag/censorship-resistance?source=post_page---footer_tags--e34e31101fc8-----------------------------------------)

[Mantle Network](https://medium.com/tag/mantle-network?source=post_page---footer_tags--e34e31101fc8-----------------------------------------)

[Ethereum](https://medium.com/tag/ethereum?source=post_page---footer_tags--e34e31101fc8-----------------------------------------)

[Bitdao](https://medium.com/tag/bitdao?source=post_page---footer_tags--e34e31101fc8-----------------------------------------)

[Bit](https://medium.com/tag/bit?source=post_page---footer_tags--e34e31101fc8-----------------------------------------)

[![Mantle Network](https://miro.medium.com/v2/resize:fill:48:48/0*w-6d4VpYha0olTgb.jpg)](https://medium.com/@mantlenetwork.eth?source=post_page---post_author_info--e34e31101fc8-----------------------------------------)

[![Mantle Network](https://miro.medium.com/v2/resize:fill:64:64/0*w-6d4VpYha0olTgb.jpg)](https://medium.com/@mantlenetwork.eth?source=post_page---post_author_info--e34e31101fc8-----------------------------------------)

[**Written by Mantle Network**](https://medium.com/@mantlenetwork.eth?source=post_page---post_author_info--e34e31101fc8-----------------------------------------)
