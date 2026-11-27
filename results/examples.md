# Qualitative examples

Counts: expansion-distractor cases 3 shown, filter helped 2, filter hurt 2.


## A. Query expansion brought in distractors


### Q: what is a coherent set of values and beliefs about public policy called
Gold answers: ['a political ideology', 'political ideology', 'ideology']

**S1 (BM25)**: answer *coherent ideology* (correct), nDCG 0.13, UDCG 0.50, hard distractors 2

1. (irrelevant, DE 0.76) *Coherence theory of truth*: system, called the ""absolute"", and that humanly knowable propositions and systems have a degree of truth that is proportionate to how fully they approximate this ideal. Perhaps the best-known objection to a coherence t... -> LLM alone says: "NO-RESPONSE"
2. (irrelevant, DE 1.00) *Japanese nationalism*: and only with a strong economy and military could Japan force a revision of the unequal treaties, such as the Kanagawa Accords. Government policies also laid the basis of later industrialist empires known as the ""zaibat... -> LLM alone says: "buke shisō"
3. (irrelevant, DE 0.21) *William Lycan*: of belief acquisition and epistemic justification. To acquire a new belief is to acquire a new real, internal representation instantiated in one’s functional architecture. And a new belief is justified if it, better than... -> LLM alone says: "NO-RESPONSE"
4. (irrelevant, DE 0.97) *Coherentism*: too."" Usually the system of belief is taken to be the complete set of beliefs of the individual or group, that is, their theory of the world. It is necessary for coherentism to explain in some detail what it means for a... -> LLM alone says: "A coherent system of values and beliefs about public policy is called a theory of public policy."
5. (RELEVANT) *Interactive acculturation*: government. But in civic ideologies, there is no public financial support for these private values or for the continuation and flourishing of the particular culture. The cultural identities and values are allowed but not... -> LLM alone says: "Civic ideology"

**S2 (Query2Doc + BM25)**: answer *Normative economics* (wrong), nDCG 0.34, UDCG 0.48, hard distractors 4

1. (RELEVANT) *Interactive acculturation*: government. But in civic ideologies, there is no public financial support for these private values or for the continuation and flourishing of the particular culture. The cultural identities and values are allowed but not... -> LLM alone says: "Civic ideology"
2. (irrelevant, DE 1.00) *Normative*: to the norms implicit in those structures) occur, while discouraging or preventing social activity that ""ought not"" occur. That is, they promote social activity that is socially ""valued"" (see philosophy above). While... -> LLM alone says: "Normative economics"
3. (irrelevant, DE 1.00) *The Idea of Justice*: follows that 'Public Reason'- i.e. open discussion and rational argument- can enable what Sen calls 'plural grounding'- i.e. an 'overlapping consensus' (in Rawls's terminology) between people of different ideologies or b... -> LLM alone says: "Overlapping consensus"
4. (irrelevant, DE 1.00) *Development communication*: intuitively reflective of perceptions and in real society than the government. It also provides an alternative set of perspective on economic trends which policymakers can use to make prudent finance policy decisions. Th... -> LLM alone says: "Policy"
5. (irrelevant, DE 1.00) *Group of Five*: set of normative and principled beliefs"", which provide a value-based rationale for the social action of community members; (b) ""shared causal beliefs"", which are derived from their analysis of practices leading or co... -> LLM alone says: "Group of Five"


### Q: who won an oscar for schindler 's list
Gold answers: ['Gerald R. Molen', 'Steven Spielberg', 'Allan Starski', 'Steven Zaillian', 'John Williams', 'Ewa Braun', 'Michael Kahn', 'Branko Lustig', 'Janusz Kamiński']

**S1 (BM25)**: answer *Steven Spielberg* (correct), nDCG 0.38, UDCG 0.58, hard distractors 0

1. (irrelevant, DE 0.36) *Oscar Schindler (horse)*: Schindlers Hunt who won five races including the Durkan New Home Novice Chase and the Arkle Novice Chase. Oscar Schindler (horse) Oscar Schindler (4 February 1992 – after 2005) was an Irish Thoroughbred racehorse and sta... -> LLM alone says: "NO-RESPONSE"
2. (RELEVANT) *California State University, Long Beach*: and VR Troopers Power Rangers. Former students have won at least five Academy Awards. Steven Spielberg (Class of 1969, BA 2002) won two Oscars for Best Directing for ""Schindler's List"" and ""Saving Private Ryan"" and h... -> LLM alone says: "Steven Spielberg"
3. (RELEVANT) *Leo Rosner*: Leo Rosner Leopold ""Leo"" Rosner (26 June 1918 – 10 October 2008) was a Polish-born Australian musician. Rosner, who was Jewish, survived the Holocaust in Nazi concentration camps during World War II by playing his acco... -> LLM alone says: "Steven Spielberg"
4. (irrelevant, DE 0.15) *Oscar Schindler (horse)*: the Kevin Prendergast. His sire, Royal Academy, won the July Cup at Newmarket and the Breeders' Cup Mile in 1990. At stud, the best of his other winners included the Sussex Stakes winner Ali-Royal and the Hong Kong champ... -> LLM alone says: "NO-RESPONSE"
5. (irrelevant, DE 0.71) *Brokeback Mountain*: film industry. Supporters of the film engendered considerable discussion after the film ""Crash"" won the Academy Award for Best Picture. Some critics accused the Academy of homophobia for failing to award the Oscar for ... -> LLM alone says: "No-RESPONSE"

**S2 (Query2Doc + BM25)**: answer *Liam Neeson* (wrong), nDCG 0.83, UDCG 0.67, hard distractors 1

1. (RELEVANT) *Oskar Schindler*: the project, and he offered the rights to several other directors. After he read a script for the project prepared by Steven Zaillian for Martin Scorsese, he decided to trade him ""Cape Fear"" for the opportunity to do t... -> LLM alone says: "Liam Neeson"
2. (RELEVANT) *47th British Academy Film Awards*: 47th British Academy Film Awards The 47th British Film Awards, given by the British Academy of Film and Television Arts in 1994, honoured the best films of 1993. Steven Spielberg's Schindler's List won the award for Best... -> LLM alone says: "No-RESPONSE"
3. (irrelevant, DE 1.00) *Steven Spielberg*: effects provided by friend George Lucas's Industrial Light & Magic company, the film would eventually become the highest-grossing film of all time (at the worldwide box office) with $914.7 million. This would be the thir... -> LLM alone says: "Steven Spielberg"
4. (RELEVANT) *Schindler's List*: Schindler's List Schindler's List is a 1993 American epic historical period drama film directed and co-produced by Steven Spielberg and written by Steven Zaillian. It is based on the novel ""Schindler's Ark"" by Australi... -> LLM alone says: "Ben Kingsley"
5. (RELEVANT) *Schindler's List*: opened in June 2010. Schindler's List Schindler's List is a 1993 American epic historical period drama film directed and co-produced by Steven Spielberg and written by Steven Zaillian. It is based on the novel ""Schindle... -> LLM alone says: "Ben Kingsley"


### Q: who wrote the song stop the world and let me off
Gold answers: ['W.S. Stevenson', 'Carl Belew']

**S1 (BM25)**: answer *Carl Belew* (correct), nDCG 0.26, UDCG 0.52, hard distractors 0

1. (irrelevant, DE 0.02) *Let Me Entertain You (Gypsy)*: described it as a ""renowned musical number."" CurtainUp calls it a ""sister act"" and ""scary,"" due to the ""frightening stage mother."" Artsnats deemed it a ""striptease reprise."" ""Stage and Cinema"" called it ""the... -> LLM alone says: "NO-RESPONSE"
2. (irrelevant, DE 0.69) *Let Me Down Easy (Roger Daltrey song)*: 11 on Billboard's Top Rock Tracks chart. When Jim Vallance was asked about the track, he recalled that they wrote the song during January 1984 and that: ""Adams and I originally wrote ""Let Me Down Easy"" for Stevie Nick... -> LLM alone says: "Bryan Adams and Jim Vallance"
3. (irrelevant, DE 0.05) *Don't Let Me Down (Leona Lewis song)*: dominated by ""thoughtless"" ballads like ""Stop Crying Your Heart Out"" and ""Don't Let Me Down"". While he noted that Lewis gives a ""technically unimpeachable"" vocal performance, he wrote that it does not compensate ... -> LLM alone says: "NO-RESPONSE"
4. (RELEVANT) *Carl Belew*: charted in the 1970s with covers of ""Stop the World and Let Me Off"". Belew died of cancer on October 31, 1990 in Salina, Oklahoma. Carl Belew Carl Robert Belew (April 21, 1931 – October 31, 1990) was an American countr... -> LLM alone says: "Johnnie & Jack"
5. (irrelevant, DE 0.76) *Don't Let Me Wait Too Long*: Don't Let Me Wait Too Long ""Don't Let Me Wait Too Long"" is a song by English rock musician George Harrison, released on his 1973 album ""Living in the Material World"". It was scheduled to be issued as a single in Sept... -> LLM alone says: "George Harrison"

**S2 (Query2Doc + BM25)**: answer *Marc Beeson and Danny Orton* (wrong), nDCG 0.61, UDCG 0.53, hard distractors 1

1. (RELEVANT) *Carl Belew*: charted in the 1970s with covers of ""Stop the World and Let Me Off"". Belew died of cancer on October 31, 1990 in Salina, Oklahoma. Carl Belew Carl Robert Belew (April 21, 1931 – October 31, 1990) was an American countr... -> LLM alone says: "Johnnie & Jack"
2. (irrelevant, DE 0.86) *Let Me (Pat Green song)*: Let Me (Pat Green song) ""Let Me"" is a song written by Marc Beeson and Danny Orton, and recorded by American country music artist Pat Green. It was released in June 2008 as the lead-off single from his album ""What I'm ... -> LLM alone says: "Marc Beeson and Danny Orton"
3. (irrelevant, DE 0.07) *I Don't Have to Be Me ('til Monday)*: Hot Country Songs) charts, peaking at number 2 in mid-2002. It was his first charting single since ""I Never Stopped Lovin' You"" in 1996. I Don't Have to Be Me ('til Monday) ""I Don't Have To Be Me ('til Monday)"" is a ... -> LLM alone says: "NO-RESPONSE"
4. (irrelevant, DE 0.16) *Let Me into Your Heart*: Let Me into Your Heart ""Let Me into Your Heart"" is a song written and recorded by American country music artist Mary Chapin Carpenter. It was released in September 1996 as the first single from the album ""A Place in t... -> LLM alone says: "NO-RESPONSE"
5. (irrelevant, DE 0.39) *Let Me into Your Heart*: of October 5, 1996. Let Me into Your Heart ""Let Me into Your Heart"" is a song written and recorded by American country music artist Mary Chapin Carpenter. It was released in September 1996 as the first single from the ... -> LLM alone says: "NO-RESPONSE"


## B. The filter helped


### Q: who wrote there 's a guy works down the chip shop lyrics
Gold answers: ['Philip Rambow', 'Kirsty MacColl / Philip Rambow', 'Kirsty MacColl']

**S4 (Query2Doc + BM25 + reranker)**: answer *Hasse Olsson* (wrong), nDCG 1.00, UDCG 0.73, hard distractors 0

1. (RELEVANT) *There's a Guy Works Down the Chip Shop Swears He's Elvis*: of the Morning"", with lyrics in Swedish by Hasse Olsson as ""Killen ner' på Konsum svär att han är Elvis"" (""The guy down Konsum"" swears he's Elvis). There's a Guy Works Down the Chip Shop Swears He's Elvis ""There's ... -> LLM alone says: "Kirsty MacColl"
2. (RELEVANT) *There's a Guy Works Down the Chip Shop Swears He's Elvis*: There's a Guy Works Down the Chip Shop Swears He's Elvis ""There's a Guy Works Down the Chip Shop Swears He's Elvis"" was Kirsty MacColl's first hit single, charting in the UK at #14 in 1981, and remaining in the charts ... -> LLM alone says: "Kirsty MacColl"
3. (RELEVANT) *Kirsty MacColl*: Kirsty MacColl Kirsty Anna MacColl (10 October 1959 – 18 December 2000) was a British singer and songwriter. She recorded several pop hits in the 1980s and 1990s, including ""There's a Guy Works Down the Chip Shop Swears... -> LLM alone says: "Billy Bragg"
4. (RELEVANT) *Discworld characters*: timeline in which this happened has, however, been eradicated following Death's intervention, and he was last seen working in a fried fish stall in Quirm, a clear reference to Kirsty MacColl's song ""There's a Guy Works ... -> LLM alone says: "Kirsty MacColl"
5. (RELEVANT) *Terry (Kirsty MacColl song)*: Terry (Kirsty MacColl song) ""Terry"" is a song by Kirsty MacColl, released as a single in October 1983, and charting at #82 in the UK the following month. It was her first release after returning to Stiff Records, and w... -> LLM alone says: "No-RESPONSE"

**S4F (Query2Doc + BM25 + reranker + filter)**: answer *Kirsty MacColl* (correct), nDCG nan, UDCG 0.73, hard distractors 0

1. (RELEVANT) *There's a Guy Works Down the Chip Shop Swears He's Elvis*: of the Morning"", with lyrics in Swedish by Hasse Olsson as ""Killen ner' på Konsum svär att han är Elvis"" (""The guy down Konsum"" swears he's Elvis). There's a Guy Works Down the Chip Shop Swears He's Elvis ""There's ... -> LLM alone says: "Kirsty MacColl"
2. (RELEVANT) *There's a Guy Works Down the Chip Shop Swears He's Elvis*: There's a Guy Works Down the Chip Shop Swears He's Elvis ""There's a Guy Works Down the Chip Shop Swears He's Elvis"" was Kirsty MacColl's first hit single, charting in the UK at #14 in 1981, and remaining in the charts ... -> LLM alone says: "Kirsty MacColl"
3. (RELEVANT) *Kirsty MacColl*: Kirsty MacColl Kirsty Anna MacColl (10 October 1959 – 18 December 2000) was a British singer and songwriter. She recorded several pop hits in the 1980s and 1990s, including ""There's a Guy Works Down the Chip Shop Swears... -> LLM alone says: "Billy Bragg" **[dropped by filter]**
4. (RELEVANT) *Discworld characters*: timeline in which this happened has, however, been eradicated following Death's intervention, and he was last seen working in a fried fish stall in Quirm, a clear reference to Kirsty MacColl's song ""There's a Guy Works ... -> LLM alone says: "Kirsty MacColl"
5. (RELEVANT) *Terry (Kirsty MacColl song)*: Terry (Kirsty MacColl song) ""Terry"" is a song by Kirsty MacColl, released as a single in October 1983, and charting at #82 in the UK the following month. It was her first release after returning to Stiff Records, and w... -> LLM alone says: "No-RESPONSE" **[dropped by filter]**


### Q: what is the final season of downton abbey
Gold answers: ['the sixth', 'sixth', 'Six', 'the sixth series', 'six']

**S4 (Query2Doc + BM25 + reranker)**: answer *Series 6* (wrong), nDCG 0.47, UDCG 0.56, hard distractors 0

1. (RELEVANT) *Downton Abbey*: both ITV and PBS, and subsequently became the most successful British costume drama series since the 1981 television serial of ""Brideshead Revisited"". On 26 March 2015, Carnival Films and ITV announced that the sixth s... -> LLM alone says: "The sixth season."
2. (irrelevant, DE 0.22) *Downton Abbey (series 2)*: Downton Abbey (series 2) The second series of the British historical period drama television series ""Downton Abbey"" aired from 18 September 2011 to 6 November 2011, comprising a total of 8 episodes and one Christmas Sp... -> LLM alone says: "NO-RESPONSE"
3. (irrelevant, DE 0.49) *Downton Abbey (film)*: Downton Abbey (film) Downton Abbey is an upcoming British historical period drama film, written by Julian Fellowes and directed by Michael Engler. It is a continuation of the television series of the same name, created b... -> LLM alone says: "NO-RESPONSE"
4. (irrelevant, DE 0.19) *Downton Abbey (series 2)*: more contrived and inconsistent than it was in its first season."" In a less enthusiastic review for the ""Washington Post"", Hank Stuever quipped, """"Downton Abbey"" lacks surprise and is stretched precariously thin, a... -> LLM alone says: "NO-RESPONSE"
5. (RELEVANT) *Matthew Goode*: chess champion. In 2014, Goode co-starred in the ITV drama ""Downton Abbey""s Season 5 Christmas special titled ""A Moorland Holiday"" as Henry Talbot. He returned to ""Downton Abbey"" in October 2015 beginning in the fo... -> LLM alone says: "NO-RESPONSE"

**S4F (Query2Doc + BM25 + reranker + filter)**: answer *The sixth season.* (correct), nDCG nan, UDCG 0.73, hard distractors 0

1. (RELEVANT) *Downton Abbey*: both ITV and PBS, and subsequently became the most successful British costume drama series since the 1981 television serial of ""Brideshead Revisited"". On 26 March 2015, Carnival Films and ITV announced that the sixth s... -> LLM alone says: "The sixth season."
2. (irrelevant, DE 0.22) *Downton Abbey (series 2)*: Downton Abbey (series 2) The second series of the British historical period drama television series ""Downton Abbey"" aired from 18 September 2011 to 6 November 2011, comprising a total of 8 episodes and one Christmas Sp... -> LLM alone says: "NO-RESPONSE" **[dropped by filter]**
3. (irrelevant, DE 0.49) *Downton Abbey (film)*: Downton Abbey (film) Downton Abbey is an upcoming British historical period drama film, written by Julian Fellowes and directed by Michael Engler. It is a continuation of the television series of the same name, created b... -> LLM alone says: "NO-RESPONSE" **[dropped by filter]**
4. (irrelevant, DE 0.19) *Downton Abbey (series 2)*: more contrived and inconsistent than it was in its first season."" In a less enthusiastic review for the ""Washington Post"", Hank Stuever quipped, """"Downton Abbey"" lacks surprise and is stretched precariously thin, a... -> LLM alone says: "NO-RESPONSE" **[dropped by filter]**
5. (RELEVANT) *Matthew Goode*: chess champion. In 2014, Goode co-starred in the ITV drama ""Downton Abbey""s Season 5 Christmas special titled ""A Moorland Holiday"" as Henry Talbot. He returned to ""Downton Abbey"" in October 2015 beginning in the fo... -> LLM alone says: "NO-RESPONSE" **[dropped by filter]**


## C. The filter hurt


### Q: who has scored more goals in the premier league
Gold answers: ['Alan Shearer']

**S4 (Query2Doc + BM25 + reranker)**: answer *Alan Shearer* (correct), nDCG 0.72, UDCG 0.61, hard distractors 2

1. (RELEVANT) *2007–08 Premier League*: The Manchester United winger's 31 goals from 34 league appearances helped see off stiff opposition for this award from Arsenal's Emmanuel Adebayor and Fernando Torres of Liverpool. This was the first Premier League seaso... -> LLM alone says: "Cristiano Ronaldo"
2. (RELEVANT) *Thierry Henry*: In terms of goal-scoring awards, Henry was the European Golden Boot winner in 2004 and 2005 (sharing it with Villarreal's Diego Forlán in 2005). Henry was also the top goalscorer in the Premier League for a record four s... -> LLM alone says: "Alan Shearer"
3. (RELEVANT) *Wayne Rooney*: League goals being the most scored by a player for any single club. Rooney's 208 Premier League goals make him the Premier League's second top scorer of all time behind only Alan Shearer. He also has the third-highest nu... -> LLM alone says: "Alan Shearer"
4. (irrelevant, DE 0.98) *Jermain Defoe*: holds the Premier League record for the most goals scored as a substitute, with 22, as of 11 January 2014. On 19 November 2016, Defoe scored his 150th Premier League goal, becoming the joint tenth-highest goal scorer in ... -> LLM alone says: "Jermain Defoe"
5. (irrelevant, DE 1.00) *Sergio Agüero*: the highest goals per minute ratio in the history of the competition since its formation in 1992, averaging a goal every 106 minutes, ahead of Thierry Henry. He also holds the joint-record for the most goals scored in a ... -> LLM alone says: "Sergio Agüero"

**S4F (Query2Doc + BM25 + reranker + filter)**: answer *Thierry Henry* (wrong), nDCG nan, UDCG 0.73, hard distractors 0

1. (RELEVANT) *2007–08 Premier League*: The Manchester United winger's 31 goals from 34 league appearances helped see off stiff opposition for this award from Arsenal's Emmanuel Adebayor and Fernando Torres of Liverpool. This was the first Premier League seaso... -> LLM alone says: "Cristiano Ronaldo" **[dropped by filter]**
2. (RELEVANT) *Thierry Henry*: In terms of goal-scoring awards, Henry was the European Golden Boot winner in 2004 and 2005 (sharing it with Villarreal's Diego Forlán in 2005). Henry was also the top goalscorer in the Premier League for a record four s... -> LLM alone says: "Alan Shearer"
3. (RELEVANT) *Wayne Rooney*: League goals being the most scored by a player for any single club. Rooney's 208 Premier League goals make him the Premier League's second top scorer of all time behind only Alan Shearer. He also has the third-highest nu... -> LLM alone says: "Alan Shearer"
4. (irrelevant, DE 0.98) *Jermain Defoe*: holds the Premier League record for the most goals scored as a substitute, with 22, as of 11 January 2014. On 19 November 2016, Defoe scored his 150th Premier League goal, becoming the joint tenth-highest goal scorer in ... -> LLM alone says: "Jermain Defoe" **[dropped by filter]**
5. (irrelevant, DE 1.00) *Sergio Agüero*: the highest goals per minute ratio in the history of the competition since its formation in 1992, averaging a goal every 106 minutes, ahead of Thierry Henry. He also holds the joint-record for the most goals scored in a ... -> LLM alone says: "Sergio Agüero" **[dropped by filter]**


### Q: fast & furious 8 release date in india
Gold answers: ['April 12 , 2017']

**S4 (Query2Doc + BM25 + reranker)**: answer *April 12, 2017* (correct), nDCG 0.63, UDCG 0.51, hard distractors 1

1. (irrelevant, DE 0.79) *The Fate of the Furious*: starring Johnson and Statham's characters is scheduled for release in August 2019. The Fate of the Furious The Fate of the Furious (alternatively known as Fast & Furious 8 and Fast 8, and often stylized as F8) is a 2017 ... -> LLM alone says: "The Fate of the Furious was released in India on April 14, 2017."
2. (RELEVANT) *The Fate of the Furious*: internationally, and received a day-and-date release across major markets such as Australia, the United Kingdom, China, and India, beginning on April 12, 2017. The film was released day-and-date in 1,074 IMAX screens aro... -> LLM alone says: "April 12, 2017"
3. (irrelevant, DE 0.30) *Fast Five*: the ""Fast and Furious"" franchise (behind ""Fast 6"" and ""Furious 7"") and the fifth highest-grossing Universal film. It was initially released in Australia on Wednesday, April 20, 2011 – nine days before the release d... -> LLM alone says: "NO-RESPONSE"
4. (irrelevant, DE 0.19) *Furious 7*: 3, 2015 (the same release date from the 2009 film ""Fast & Furious""). The official announcement in change of date was made in July 2014. ""Furious 7"" premiered at the SXSW Film Festival at 12:07 a.m. at Austin's Paramo... -> LLM alone says: "NO-RESPONSE"
5. (irrelevant, DE 0.82) *Furious 7*: it has to be as good as or better [than ""Furious 7""]"". At the 2015 CinemaCon in Las Vegas, Diesel announced the film for an April 14, 2017 release date. On August 16, 2015, at the 2015 Teen Choice Awards (where ""Furi... -> LLM alone says: "The release date for Fast & Furious 8 in India was April 14, 2017."

**S4F (Query2Doc + BM25 + reranker + filter)**: answer *The Fate of the Furious was released in India on April 14, 2017.* (wrong), nDCG nan, UDCG 0.43, hard distractors 0

1. (irrelevant, DE 0.79) *The Fate of the Furious*: starring Johnson and Statham's characters is scheduled for release in August 2019. The Fate of the Furious The Fate of the Furious (alternatively known as Fast & Furious 8 and Fast 8, and often stylized as F8) is a 2017 ... -> LLM alone says: "The Fate of the Furious was released in India on April 14, 2017."
2. (RELEVANT) *The Fate of the Furious*: internationally, and received a day-and-date release across major markets such as Australia, the United Kingdom, China, and India, beginning on April 12, 2017. The film was released day-and-date in 1,074 IMAX screens aro... -> LLM alone says: "April 12, 2017" **[dropped by filter]**
3. (irrelevant, DE 0.30) *Fast Five*: the ""Fast and Furious"" franchise (behind ""Fast 6"" and ""Furious 7"") and the fifth highest-grossing Universal film. It was initially released in Australia on Wednesday, April 20, 2011 – nine days before the release d... -> LLM alone says: "NO-RESPONSE" **[dropped by filter]**
4. (irrelevant, DE 0.19) *Furious 7*: 3, 2015 (the same release date from the 2009 film ""Fast & Furious""). The official announcement in change of date was made in July 2014. ""Furious 7"" premiered at the SXSW Film Festival at 12:07 a.m. at Austin's Paramo... -> LLM alone says: "NO-RESPONSE" **[dropped by filter]**
5. (irrelevant, DE 0.82) *Furious 7*: it has to be as good as or better [than ""Furious 7""]"". At the 2015 CinemaCon in Las Vegas, Diesel announced the film for an April 14, 2017 release date. On August 16, 2015, at the 2015 Teen Choice Awards (where ""Furi... -> LLM alone says: "The release date for Fast & Furious 8 in India was April 14, 2017." **[dropped by filter]**
