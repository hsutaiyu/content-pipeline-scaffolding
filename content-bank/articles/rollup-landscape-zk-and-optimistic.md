---
title: "Diving into the Rollup Landscape: Zero-Knowledge and Optimistic"
source: https://medium.com/0xmantle/diving-into-the-rollup-landscape-zero-knowledge-and-optimistic-c1833efcceb2
published: 2023-03-17
note: Writing sample for voice reference.
---

# **Diving into the Rollup Landscape: Zero-Knowledge and Optimistic**

[![Mantle Network](https://miro.medium.com/v2/resize:fill:32:32/0*w-6d4VpYha0olTgb.jpg)](https://medium.com/@mantlenetwork.eth?source=post_page---byline--c1833efcceb2-----------------------------------------)

[Mantle Network](https://medium.com/@mantlenetwork.eth?source=post_page---byline--c1833efcceb2-----------------------------------------)

Mar 17, 2023

494

4

Layer-2 (L2) rollups have been firmly established as the driving force for Ethereum scaling. As the first to reach the market, optimistic rollups have dominated the L2 playing field. Zero-knowledge (ZK) rollups, long on the horizon due to the complexity of solving EVM compatibility, are now poised to enter the scene. With this in mind, BitDAO is considering a proposal to develop a zkEVM version of Mantle Mainnet alongside the current optimistic build. This article aims to compare and contrast optimistic and ZK rollups, and gives further context to the discussion of incorporating ZK technology into the Mantle stack.

### **Rollup Basics**

Both types of rollups accomplish Ethereum scaling by lessening the burden of transaction processing on Layer 1 (L1). By batching large chunks of transactions on the L2 chain and delivering those batches to Ethereum, rollups reduce the workload of the main chain. Moving the bulk of user activity to L2 means the only operations taking place on Ethereum are:

- Processing deposits and withdrawals
- Verifying that the activity on a rollup is following the L1 ruleset

These interactions are done through an L1 smart contract, which acts as an anchor. The verification is accomplished through **proofs** submitted by the rollup, which brings us to the core difference between optimistic and ZK rollups.

_For a deeper dive into Ethereum rollups, see Vitalik Buterin’s “_ [_An Incomplete Guide to Rollups_](https://vitalik.ca/general/2021/01/05/rollup.html) _”_

### **Optimistic Rollup Design**

What makes a rollup “optimistic”? The name relates to how this type of L2 interacts with the Ethereum network and what type of proofs are used to verify the data it sends over. Optimistic rollups work on the assumption that transaction data sent to L1 is valid; however, any network participant can challenge the validity of a block by submitting a fraud proof.

Once the challenge process has been initiated, the transactions in question will be re-submitted, this time directly on L1, to confirm or deny validity. The block proposer in question will have previously staked ETH as a network requirement, which could be slashed if they are found to have broken the rules. Similarly, the challenger is required to put up a stake when submitting a fraud proof, which serves to disincentivize unfounded accusations.

## Get Mantle Network’s stories in your inbox

The current standard for optimistic rollups is a seven-day challenge period, making slow time to finality for an issue. The challenge system also requires the vigilance of network participants to report flagrant actions, and fraud proofs can sometimes be too large to include all relevant data. Despite its flaws, the optimistic design has worked well in practice, with adoption for leading chains like Arbitrum and Optimism seeing sustained growth.

### **Zk Rollup Design**

ZK rollups utilize ZK proofs to verify the transaction data that is sent to L1, hence the name. These cryptographic proofs, succinct non-interactive arguments of knowledge (known as SNARKs), are sent along with each batch of transactions, ensuring validity without revealing the data in question. Unlike optimistic rollups, there is no need for network participants to monitor others’ behavior in a ZK rollup. Verification can be achieved almost instantly after the proof has been generated, making finality on a ZK rollup much faster than on its optimistic counterpart. The fact that this validation method doesn’t require revealing the underlying transaction data also makes ZK rollups optimal for user privacy.

### **Trade-Offs**

Similar to any blockchain, speed, cost, and security are the primary areas to consider when evaluating a rollup. The design differences outlined above create trade-offs between each of these aspects. ZK rollups are inherently more secure due to the ZK proofs being passed with each batch of transactions, but the inclusion of the proof results in higher gas cost per batch. Fixed gas costs for a batch of optimistic rollup transactions sits at around 40,000 gas, while a ZK rollup batch is around 500,000. While ZK rollup batches cost more gas because of the proof, the cost per transaction is much lower than that of an optimistic rollup batch. This allows more transactions to be included in each batch, giving ZK rollups a distinct advantage when it comes to throughput. The ceiling is about 2000 TPS vs. 500 for an optimistic rollup.

Privacy can also be considered an element of security, which favors ZK rollups and their ability to process transactions confidentially. There is a possibility that optimistic rollups can implement privacy layers, but they are not confidential by default.

Differences in time to finality are also experienced on the user end, as withdrawals from optimistic rollups take seven days due to the necessary challenge period. Since ZK proofs offer instant finality, withdrawals can be made as soon as the next batch of transactions is sent out.

Finality aside, transaction settlement within an optimistic rollup is generally relatively fast, as new blocks are generated in a matter of seconds. ZK proofs are more computationally intensive and can take anywhere from seconds up to 20 minutes, depending on the specific hardware used.

### **Current State of L2s**

While ZK rollups are quite impressive when it comes to solving the blockchain trilemma, they have so far been held back by incompatibility with Ethereum. Optimistic rollups are currently much more prominent due to the innovation of the Optimistic Virtual Machine (OVM). It supports Solidity and is entirely compliant with Ethereum, allowing smart contracts and dApps to be easily transferable from layer 1 to an optimistic rollup. The development of a zkEVM is essential to bringing about the next wave of rollups, with several major players planning to roll out their versions in 2023.

As a new entrant into the world of L2s, Mantle is dedicated to the future of Ethereum scaling, for which the ZK stack presents a significant opportunity. This is the impetus behind the recent BitDAO proposal to explore a zkEVM network for Mantle. The premise of rollups is to optimize the user experience on Ethereum, and incorporating ZK tech promises future advantages in throughput, security, and speed.

While the deployment of a fully functional zkEVM on mainnet is yet to be seen, recent developments in the zkEVM space offer great research value — Mantle is well positioned to potentially drive a ready zkEVM alternative soon to its Mantle Optimistic network, which is currently available on Mantle’s testnet.

### **The Choice is Yours**

Tell us what benefits or challenges you are facing with ZK or optimistic rollups on the zkEVM research proposal on the [BitDAO Forum](https://discourse.bitdao.io/t/discussion-mantle-zkevm-research-industry-collaboration/4699). Open and active community discussion on the topic will help Mantle to deliver a network that is built for and created with the help of builders.

[Ethereum](https://medium.com/tag/ethereum?source=post_page---footer_tags--c1833efcceb2-----------------------------------------)

[Optimistic Rollup](https://medium.com/tag/optimistic-rollup?source=post_page---footer_tags--c1833efcceb2-----------------------------------------)

[Zkrollup](https://medium.com/tag/zkrollup?source=post_page---footer_tags--c1833efcceb2-----------------------------------------)

[Layer 2](https://medium.com/tag/layer-2?source=post_page---footer_tags--c1833efcceb2-----------------------------------------)

[L2](https://medium.com/tag/l2?source=post_page---footer_tags--c1833efcceb2-----------------------------------------)

[![Mantle Network](https://miro.medium.com/v2/resize:fill:48:48/0*w-6d4VpYha0olTgb.jpg)](https://medium.com/@mantlenetwork.eth?source=post_page---post_author_info--c1833efcceb2-----------------------------------------)

[![Mantle Network](https://miro.medium.com/v2/resize:fill:64:64/0*w-6d4VpYha0olTgb.jpg)](https://medium.com/@mantlenetwork.eth?source=post_page---post_author_info--c1833efcceb2-----------------------------------------)

[**Written by Mantle Network**](https://medium.com/@mantlenetwork.eth?source=post_page---post_author_info--c1833efcceb2-----------------------------------------)
