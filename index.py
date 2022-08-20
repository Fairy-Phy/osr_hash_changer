import hashlib
import os
import re

print("osr情報変更プログラム")
while True:
	print()

	osr_path = input("変更対象のリプレイ(.osr)ファイルパス: ")
	change_hash_osu_path = input("変更するときの譜面(.osu)ファイルパス: ")

	if not osr_path or not change_hash_osu_path:
		print("パスが入力されてません")
		continue

	osr_path = re.sub(r"^(?:'|\")(.*)(?:'|\")$", "\\1", osr_path)
	change_hash_osu_path = re.sub(r"^(?:'|\")(.*)(?:'|\")$", "\\1", change_hash_osu_path)

	if os.path.splitext(osr_path)[-1] != ".osr":
		print("osrファイルではありません")
		continue
	if os.path.splitext(change_hash_osu_path)[-1] != ".osu":
		print("osuファイルではありません")
		continue

	if not os.path.isfile(osr_path) or not os.path.isfile(osr_path):
		print("有効なパスではないかファイルではありません")
		continue

	print("(オプション) 名前を変更できます、何も入力しない場合は変更しません")
	change_name = input("ユーザー名: ")

	print("変換を開始します")

	bytes_ = []
	with open(osr_path, mode="rb") as binary_file:
		bn = binary_file.read(5)
		print("mode, makeversion:", bn)
		bytes_.extend(list(bn))

		# hash section
		bn = binary_file.read(1)
		print("strstart:", bn)
		if bn[0] != 0x0b:
			print("バグった")
			raise Exception()
		bytes_.extend(list(bn))

		hash_bn = 0
		shift = 0
		while True:
			bn_0 = binary_file.read(1)[0]
			hash_bn |= (bn_0 & 0x7f) << shift
			if (bn_0 & 0x80) == 0:
				break
			shift += 7

		bn = binary_file.read(hash_bn)
		print("prevhash:", bn.decode("utf8"))

		with open(change_hash_osu_path, mode="rb") as osu_file:
			change_hash = hashlib.md5(osu_file.read())
			change_hash_size = change_hash.digest_size * 2
			change_hash_bytes = change_hash.hexdigest().encode("utf8")
			print("changehash:", change_hash.hexdigest())

			change_hash_length_array = list()
			while True:
				hash_size_byte = change_hash_size & 0x7f
				change_hash_size >>= 7
				if change_hash_size == 0:
					change_hash_length_array.append(hash_size_byte)
					break
				change_hash_length_array.append(hash_size_byte | 0x80)

			bytes_.extend(change_hash_length_array)
			bytes_.extend(list(change_hash_bytes))

		# name section
		if change_name and len(change_name) != 0:

			bn = binary_file.read(1)
			print("strstart:", bn)
			if bn[0] != 0x0b:
				print("バグった")
				raise Exception()
			bytes_.extend(list(bn))

			hash_bn = 0
			shift = 0
			while True:
				bn_0 = binary_file.read(1)[0]
				hash_bn |= (bn_0 & 0x7f) << shift
				if (bn_0 & 0x80) == 0:
					break
				shift += 7

			bn = binary_file.read(hash_bn)
			print("prevname:", bn.decode("utf8"))
			print("changename:", change_name)

			change_name_length_array = list()
			change_name_length = len(change_name.encode("utf8"))
			while True:
				name_length_byte = change_name_length & 0x7f
				change_name_length >>= 7
				if change_name_length == 0:
					change_name_length_array.append(name_length_byte)
					break
				change_name_length_array.append(name_length_byte | 0x80)

			bytes_.extend(change_name_length_array)
			bytes_.extend(list(change_name.encode("utf8")))

		# finalize
		bytes_.extend(list(binary_file.read()))

	osr_split = os.path.splitext(osr_path)
	export_path = osr_split[0] + "_changed" + osr_split[1]
	with open(export_path, "wb") as export:
		export.write(bytearray(bytes_))

	print("完了しました！以下のパスに保存されています")
	print(export_path)
