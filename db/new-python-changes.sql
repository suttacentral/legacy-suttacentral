ALTER TABLE collection_language ADD COLUMN language_code CHAR(2) NOT NULL;
UPDATE collection_language SET language_code = 'pi' WHERE collection_language_abbrev_name = 'Pali';
UPDATE collection_language SET language_code = 'zh' WHERE collection_language_abbrev_name = 'Chin';
UPDATE collection_language SET language_code = 'bo' WHERE collection_language_abbrev_name = 'Tib';
UPDATE collection_language SET language_code = 'sa' WHERE collection_language_abbrev_name = 'Skt';
UPDATE collection_language SET language_code = 'en' WHERE collection_language_abbrev_name = 'Oth';
UPDATE sutta SET collection_language_id = 3 WHERE collection_language_id = 7;

-- Fix NULL subdivision_uid rows in subdivision (Bug 42)
UPDATE subdivision SET subdivision_uid = 'vv' WHERE subdivision_id = 75;
UPDATE subdivision SET subdivision_uid = 'pv' WHERE subdivision_id = 76;
UPDATE subdivision SET subdivision_uid = 'thag' WHERE subdivision_id = 77;
UPDATE subdivision SET subdivision_uid = 'thig' WHERE subdivision_id = 78;
UPDATE subdivision SET subdivision_uid = 'jat' WHERE subdivision_id = 79;
UPDATE subdivision SET subdivision_uid = 'nm' WHERE subdivision_id = 80;
UPDATE subdivision SET subdivision_uid = 'ps' WHERE subdivision_id = 81;
UPDATE subdivision SET subdivision_uid = 'ap' WHERE subdivision_id = 82;
UPDATE subdivision SET subdivision_uid = 'bv' WHERE subdivision_id = 83;
UPDATE subdivision SET subdivision_uid = 'cp' WHERE subdivision_id = 84;
UPDATE subdivision SET subdivision_uid = 'prv-nosub' WHERE subdivision_id = 87;
UPDATE subdivision SET subdivision_uid = 'svbh-nosub' WHERE subdivision_id = 88;
UPDATE subdivision SET subdivision_uid = 'dhs-nosub' WHERE subdivision_id = 89;
UPDATE subdivision SET subdivision_uid = 'vbh-nosub' WHERE subdivision_id = 90;
UPDATE subdivision SET subdivision_uid = 'dhatuk-nosub' WHERE subdivision_id = 91;
UPDATE subdivision SET subdivision_uid = 'pp-nosub' WHERE subdivision_id = 92;
UPDATE subdivision SET subdivision_uid = 'kv-nosub' WHERE subdivision_id = 93;
UPDATE subdivision SET subdivision_uid = 'yam-nosub' WHERE subdivision_id = 94;
UPDATE subdivision SET subdivision_uid = 'patth-nosub' WHERE subdivision_id = 95;
UPDATE subdivision SET subdivision_uid = 'dq-nosub' WHERE subdivision_id = 179;
UPDATE subdivision SET subdivision_uid = 'up-nosub' WHERE subdivision_id = 180;
UPDATE subdivision SET subdivision_uid = 'avs-nosub' WHERE subdivision_id = 185;
UPDATE subdivision SET subdivision_uid = 'div-nosub' WHERE subdivision_id = 187;
UPDATE subdivision SET subdivision_uid = 'lal-nosub' WHERE subdivision_id = 188;
UPDATE subdivision SET subdivision_uid = 'mvu-nosub' WHERE subdivision_id = 189;
UPDATE subdivision SET subdivision_uid = 'sbh-nosub' WHERE subdivision_id = 190;
UPDATE subdivision SET subdivision_uid = 'sht10' WHERE subdivision_id = 203;

-- Fix missing or incorrect paths for these suttas (Bug 48)
UPDATE sutta
    SET sutta_text_url_link = '/dn24/pi'
    WHERE sutta_id=24;
UPDATE sutta
    SET sutta_text_url_link = '/it1/pi'
    WHERE sutta_id=8583;
UPDATE sutta
    SET sutta_text_url_link = '/it10/pi'
    WHERE sutta_id=8592;
UPDATE sutta
    SET sutta_text_url_link = '/it100/pi'
    WHERE sutta_id=8682;
UPDATE sutta
    SET sutta_text_url_link = '/it101/pi'
    WHERE sutta_id=8683;
UPDATE sutta
    SET sutta_text_url_link = '/it102/pi'
    WHERE sutta_id=8684;
UPDATE sutta
    SET sutta_text_url_link = '/it103/pi'
    WHERE sutta_id=8685;
UPDATE sutta
    SET sutta_text_url_link = '/it104/pi'
    WHERE sutta_id=8686;
UPDATE sutta
    SET sutta_text_url_link = '/it105/pi'
    WHERE sutta_id=8687;
UPDATE sutta
    SET sutta_text_url_link = '/it106/pi'
    WHERE sutta_id=8688;
UPDATE sutta
    SET sutta_text_url_link = '/it107/pi'
    WHERE sutta_id=8689;
UPDATE sutta
    SET sutta_text_url_link = '/it108/pi'
    WHERE sutta_id=8690;
UPDATE sutta
    SET sutta_text_url_link = '/it109/pi'
    WHERE sutta_id=8691;
UPDATE sutta
    SET sutta_text_url_link = '/it11/pi'
    WHERE sutta_id=8593;
UPDATE sutta
    SET sutta_text_url_link = '/it110/pi'
    WHERE sutta_id=8692;
UPDATE sutta
    SET sutta_text_url_link = '/it111/pi'
    WHERE sutta_id=8693;
UPDATE sutta
    SET sutta_text_url_link = '/it112/pi'
    WHERE sutta_id=8694;
UPDATE sutta
    SET sutta_text_url_link = '/it12/pi'
    WHERE sutta_id=8594;
UPDATE sutta
    SET sutta_text_url_link = '/it13/pi'
    WHERE sutta_id=8595;
UPDATE sutta
    SET sutta_text_url_link = '/it14/pi'
    WHERE sutta_id=8596;
UPDATE sutta
    SET sutta_text_url_link = '/it15/pi'
    WHERE sutta_id=8597;
UPDATE sutta
    SET sutta_text_url_link = '/it16/pi'
    WHERE sutta_id=8598;
UPDATE sutta
    SET sutta_text_url_link = '/it17/pi'
    WHERE sutta_id=8599;
UPDATE sutta
    SET sutta_text_url_link = '/it18/pi'
    WHERE sutta_id=8600;
UPDATE sutta
    SET sutta_text_url_link = '/it19/pi'
    WHERE sutta_id=8601;
UPDATE sutta
    SET sutta_text_url_link = '/it2/pi'
    WHERE sutta_id=8584;
UPDATE sutta
    SET sutta_text_url_link = '/it20/pi'
    WHERE sutta_id=8602;
UPDATE sutta
    SET sutta_text_url_link = '/it21/pi'
    WHERE sutta_id=8603;
UPDATE sutta
    SET sutta_text_url_link = '/it22/pi'
    WHERE sutta_id=8604;
UPDATE sutta
    SET sutta_text_url_link = '/it23/pi'
    WHERE sutta_id=8605;
UPDATE sutta
    SET sutta_text_url_link = '/it24/pi'
    WHERE sutta_id=8606;
UPDATE sutta
    SET sutta_text_url_link = '/it25/pi'
    WHERE sutta_id=8607;
UPDATE sutta
    SET sutta_text_url_link = '/it26/pi'
    WHERE sutta_id=8608;
UPDATE sutta
    SET sutta_text_url_link = '/it27/pi'
    WHERE sutta_id=8609;
UPDATE sutta
    SET sutta_text_url_link = '/it28/pi'
    WHERE sutta_id=8610;
UPDATE sutta
    SET sutta_text_url_link = '/it29/pi'
    WHERE sutta_id=8611;
UPDATE sutta
    SET sutta_text_url_link = '/it3/pi'
    WHERE sutta_id=8585;
UPDATE sutta
    SET sutta_text_url_link = '/it30/pi'
    WHERE sutta_id=8612;
UPDATE sutta
    SET sutta_text_url_link = '/it31/pi'
    WHERE sutta_id=8613;
UPDATE sutta
    SET sutta_text_url_link = '/it32/pi'
    WHERE sutta_id=8614;
UPDATE sutta
    SET sutta_text_url_link = '/it33/pi'
    WHERE sutta_id=8615;
UPDATE sutta
    SET sutta_text_url_link = '/it34/pi'
    WHERE sutta_id=8616;
UPDATE sutta
    SET sutta_text_url_link = '/it35/pi'
    WHERE sutta_id=8617;
UPDATE sutta
    SET sutta_text_url_link = '/it36/pi'
    WHERE sutta_id=8618;
UPDATE sutta
    SET sutta_text_url_link = '/it37/pi'
    WHERE sutta_id=8619;
UPDATE sutta
    SET sutta_text_url_link = '/it38/pi'
    WHERE sutta_id=8620;
UPDATE sutta
    SET sutta_text_url_link = '/it39/pi'
    WHERE sutta_id=8621;
UPDATE sutta
    SET sutta_text_url_link = '/it4/pi'
    WHERE sutta_id=8586;
UPDATE sutta
    SET sutta_text_url_link = '/it40/pi'
    WHERE sutta_id=8622;
UPDATE sutta
    SET sutta_text_url_link = '/it41/pi'
    WHERE sutta_id=8623;
UPDATE sutta
    SET sutta_text_url_link = '/it42/pi'
    WHERE sutta_id=8624;
UPDATE sutta
    SET sutta_text_url_link = '/it43/pi'
    WHERE sutta_id=8625;
UPDATE sutta
    SET sutta_text_url_link = '/it44/pi'
    WHERE sutta_id=8626;
UPDATE sutta
    SET sutta_text_url_link = '/it45/pi'
    WHERE sutta_id=8627;
UPDATE sutta
    SET sutta_text_url_link = '/it46/pi'
    WHERE sutta_id=8628;
UPDATE sutta
    SET sutta_text_url_link = '/it47/pi'
    WHERE sutta_id=8629;
UPDATE sutta
    SET sutta_text_url_link = '/it48/pi'
    WHERE sutta_id=8630;
UPDATE sutta
    SET sutta_text_url_link = '/it49/pi'
    WHERE sutta_id=8631;
UPDATE sutta
    SET sutta_text_url_link = '/it5/pi'
    WHERE sutta_id=8587;
UPDATE sutta
    SET sutta_text_url_link = '/it50/pi'
    WHERE sutta_id=8632;
UPDATE sutta
    SET sutta_text_url_link = '/it51/pi'
    WHERE sutta_id=8633;
UPDATE sutta
    SET sutta_text_url_link = '/it52/pi'
    WHERE sutta_id=8634;
UPDATE sutta
    SET sutta_text_url_link = '/it53/pi'
    WHERE sutta_id=8635;
UPDATE sutta
    SET sutta_text_url_link = '/it54/pi'
    WHERE sutta_id=8636;
UPDATE sutta
    SET sutta_text_url_link = '/it55/pi'
    WHERE sutta_id=8637;
UPDATE sutta
    SET sutta_text_url_link = '/it56/pi'
    WHERE sutta_id=8638;
UPDATE sutta
    SET sutta_text_url_link = '/it57/pi'
    WHERE sutta_id=8639;
UPDATE sutta
    SET sutta_text_url_link = '/it58/pi'
    WHERE sutta_id=8640;
UPDATE sutta
    SET sutta_text_url_link = '/it59/pi'
    WHERE sutta_id=8641;
UPDATE sutta
    SET sutta_text_url_link = '/it6/pi'
    WHERE sutta_id=8588;
UPDATE sutta
    SET sutta_text_url_link = '/it60/pi'
    WHERE sutta_id=8642;
UPDATE sutta
    SET sutta_text_url_link = '/it61/pi'
    WHERE sutta_id=8643;
UPDATE sutta
    SET sutta_text_url_link = '/it62/pi'
    WHERE sutta_id=8644;
UPDATE sutta
    SET sutta_text_url_link = '/it63/pi'
    WHERE sutta_id=8645;
UPDATE sutta
    SET sutta_text_url_link = '/it64/pi'
    WHERE sutta_id=8646;
UPDATE sutta
    SET sutta_text_url_link = '/it65/pi'
    WHERE sutta_id=8647;
UPDATE sutta
    SET sutta_text_url_link = '/it66/pi'
    WHERE sutta_id=8648;
UPDATE sutta
    SET sutta_text_url_link = '/it67/pi'
    WHERE sutta_id=8649;
UPDATE sutta
    SET sutta_text_url_link = '/it68/pi'
    WHERE sutta_id=8650;
UPDATE sutta
    SET sutta_text_url_link = '/it69/pi'
    WHERE sutta_id=8651;
UPDATE sutta
    SET sutta_text_url_link = '/it7/pi'
    WHERE sutta_id=8589;
UPDATE sutta
    SET sutta_text_url_link = '/it70/pi'
    WHERE sutta_id=8652;
UPDATE sutta
    SET sutta_text_url_link = '/it71/pi'
    WHERE sutta_id=8653;
UPDATE sutta
    SET sutta_text_url_link = '/it72/pi'
    WHERE sutta_id=8654;
UPDATE sutta
    SET sutta_text_url_link = '/it73/pi'
    WHERE sutta_id=8655;
UPDATE sutta
    SET sutta_text_url_link = '/it74/pi'
    WHERE sutta_id=8656;
UPDATE sutta
    SET sutta_text_url_link = '/it75/pi'
    WHERE sutta_id=8657;
UPDATE sutta
    SET sutta_text_url_link = '/it76/pi'
    WHERE sutta_id=8658;
UPDATE sutta
    SET sutta_text_url_link = '/it77/pi'
    WHERE sutta_id=8659;
UPDATE sutta
    SET sutta_text_url_link = '/it78/pi'
    WHERE sutta_id=8660;
UPDATE sutta
    SET sutta_text_url_link = '/it79/pi'
    WHERE sutta_id=8661;
UPDATE sutta
    SET sutta_text_url_link = '/it8/pi'
    WHERE sutta_id=8590;
UPDATE sutta
    SET sutta_text_url_link = '/it80/pi'
    WHERE sutta_id=8662;
UPDATE sutta
    SET sutta_text_url_link = '/it81/pi'
    WHERE sutta_id=8663;
UPDATE sutta
    SET sutta_text_url_link = '/it82/pi'
    WHERE sutta_id=8664;
UPDATE sutta
    SET sutta_text_url_link = '/it83/pi'
    WHERE sutta_id=8665;
UPDATE sutta
    SET sutta_text_url_link = '/it84/pi'
    WHERE sutta_id=8666;
UPDATE sutta
    SET sutta_text_url_link = '/it85/pi'
    WHERE sutta_id=8667;
UPDATE sutta
    SET sutta_text_url_link = '/it86/pi'
    WHERE sutta_id=8668;
UPDATE sutta
    SET sutta_text_url_link = '/it87/pi'
    WHERE sutta_id=8669;
UPDATE sutta
    SET sutta_text_url_link = '/it88/pi'
    WHERE sutta_id=8670;
UPDATE sutta
    SET sutta_text_url_link = '/it89/pi'
    WHERE sutta_id=8671;
UPDATE sutta
    SET sutta_text_url_link = '/it9/pi'
    WHERE sutta_id=8591;
UPDATE sutta
    SET sutta_text_url_link = '/it90/pi'
    WHERE sutta_id=8672;
UPDATE sutta
    SET sutta_text_url_link = '/it91/pi'
    WHERE sutta_id=8673;
UPDATE sutta
    SET sutta_text_url_link = '/it92/pi'
    WHERE sutta_id=8674;
UPDATE sutta
    SET sutta_text_url_link = '/it93/pi'
    WHERE sutta_id=8675;
UPDATE sutta
    SET sutta_text_url_link = '/it94/pi'
    WHERE sutta_id=8676;
UPDATE sutta
    SET sutta_text_url_link = '/it95/pi'
    WHERE sutta_id=8677;
UPDATE sutta
    SET sutta_text_url_link = '/it96/pi'
    WHERE sutta_id=8678;
UPDATE sutta
    SET sutta_text_url_link = '/it97/pi'
    WHERE sutta_id=8679;
UPDATE sutta
    SET sutta_text_url_link = '/it98/pi'
    WHERE sutta_id=8680;
UPDATE sutta
    SET sutta_text_url_link = '/it99/pi'
    WHERE sutta_id=8681;
UPDATE sutta
    SET sutta_text_url_link = '/snp5.1/pi'
    WHERE sutta_id=8749;
UPDATE sutta
    SET sutta_text_url_link = '/snp5.18/pi'
    WHERE sutta_id=8766;
UPDATE sutta
    SET sutta_text_url_link = '/snp5.19/pi'
    WHERE sutta_id=8767;
